import subprocess


def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"

patch = r"""
set -euo pipefail
cd """ + repo + r"""

FUSED=third_part/GPEN/face_model/op/fused_act.py
UPFIR=third_part/GPEN/face_model/op/upfirdn2d.py

ts=$(date -u +%Y%m%d_%H%M%S)
cp -f "$FUSED" "${FUSED}.bak_${ts}"
cp -f "$UPFIR" "${UPFIR}.bak_${ts}"

cat > "$FUSED" <<'PY'
import os
import platform

import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Function
from torch.utils.cpp_extension import load

# NOTE:
# The upstream GPEN code JIT-compiles CUDA/C++ extensions (StyleGAN2 fused ops) at import time.
# On many servers, the NVIDIA driver is present but the full CUDA toolkit is not (nvcc/cicc),
# which makes import fail and blocks inference entirely.
#
# Default here is SAFE/FALLBACK mode: do not attempt JIT compilation unless explicitly enabled.
# Set env var `GPEN_ENABLE_JIT_EXT=1` to try compiling the extension.

FUSED_AVAILABLE = False
fused = None

if (
    os.environ.get("GPEN_ENABLE_JIT_EXT", "0") == "1"
    and platform.system() == "Linux"
    and torch.cuda.is_available()
):
    try:
        module_path = os.path.dirname(__file__)
        fused = load(
            "fused",
            sources=[
                os.path.join(module_path, "fused_bias_act.cpp"),
                os.path.join(module_path, "fused_bias_act_kernel.cu"),
            ],
            verbose=False,
        )
        FUSED_AVAILABLE = True
    except Exception as e:
        # Fall back to pure PyTorch path.
        print(f"[WARN] GPEN fused extension build failed, using fallback: {type(e).__name__}: {e}")
        fused = None
        FUSED_AVAILABLE = False


class FusedLeakyReLUFunctionBackward(Function):
    @staticmethod
    def forward(ctx, grad_output, out, negative_slope, scale):
        ctx.save_for_backward(out)
        ctx.negative_slope = negative_slope
        ctx.scale = scale

        empty = grad_output.new_empty(0)

        grad_input = fused.fused_bias_act(  # type: ignore[union-attr]
            grad_output, empty, out, 3, 1, negative_slope, scale
        )

        dim = [0]
        if grad_input.ndim > 2:
            dim += list(range(2, grad_input.ndim))

        grad_bias = grad_input.sum(dim).detach()
        return grad_input, grad_bias

    @staticmethod
    def backward(ctx, gradgrad_input, gradgrad_bias):
        (out,) = ctx.saved_tensors
        gradgrad_out = fused.fused_bias_act(  # type: ignore[union-attr]
            gradgrad_input, gradgrad_bias, out, 3, 1, ctx.negative_slope, ctx.scale
        )

        return gradgrad_out, None, None, None


class FusedLeakyReLUFunction(Function):
    @staticmethod
    def forward(ctx, input, bias, negative_slope, scale):
        empty = input.new_empty(0)
        out = fused.fused_bias_act(input, bias, empty, 3, 0, negative_slope, scale)  # type: ignore[union-attr]
        ctx.save_for_backward(out)
        ctx.negative_slope = negative_slope
        ctx.scale = scale

        return out

    @staticmethod
    def backward(ctx, grad_output):
        (out,) = ctx.saved_tensors

        grad_input, grad_bias = FusedLeakyReLUFunctionBackward.apply(
            grad_output, out, ctx.negative_slope, ctx.scale
        )

        return grad_input, grad_bias, None, None


class FusedLeakyReLU(nn.Module):
    def __init__(self, channel, negative_slope=0.2, scale=2**0.5, device="cpu"):
        super().__init__()
        self.bias = nn.Parameter(torch.zeros(channel))
        self.negative_slope = negative_slope
        self.scale = scale
        self.device = device

    def forward(self, input):
        return fused_leaky_relu(input, self.bias, self.negative_slope, self.scale, self.device)


def fused_leaky_relu(input, bias, negative_slope=0.2, scale=2**0.5, device="cpu"):
    if (
        FUSED_AVAILABLE
        and platform.system() == "Linux"
        and torch.cuda.is_available()
        and device != "cpu"
    ):
        return FusedLeakyReLUFunction.apply(input, bias, negative_slope, scale)

    # Fallback works on both CPU and CUDA tensors (no custom extension required).
    return scale * F.leaky_relu(
        input + bias.view((1, -1) + (1,) * (len(input.shape) - 2)),
        negative_slope=negative_slope,
    )
PY

cat > "$UPFIR" <<'PY'
import os
import platform

import torch
import torch.nn.functional as F
from torch.autograd import Function
from torch.utils.cpp_extension import load

# See fused_act.py for rationale.
# Default: do not JIT-compile CUDA extension unless explicitly enabled.

UPFIRDN_AVAILABLE = False
upfirdn2d_op = None

if (
    os.environ.get("GPEN_ENABLE_JIT_EXT", "0") == "1"
    and platform.system() == "Linux"
    and torch.cuda.is_available()
):
    try:
        module_path = os.path.dirname(__file__)
        upfirdn2d_op = load(
            "upfirdn2d",
            sources=[
                os.path.join(module_path, "upfirdn2d.cpp"),
                os.path.join(module_path, "upfirdn2d_kernel.cu"),
            ],
            verbose=False,
        )
        UPFIRDN_AVAILABLE = True
    except Exception as e:
        print(f"[WARN] GPEN upfirdn2d extension build failed, using fallback: {type(e).__name__}: {e}")
        upfirdn2d_op = None
        UPFIRDN_AVAILABLE = False


class UpFirDn2dBackward(Function):
    @staticmethod
    def forward(ctx, grad_output, kernel, grad_kernel, up, down, pad, g_pad, in_size, out_size):
        up_x, up_y = up
        down_x, down_y = down
        g_pad_x0, g_pad_x1, g_pad_y0, g_pad_y1 = g_pad

        grad_output = grad_output.reshape(-1, out_size[0], out_size[1], 1)

        grad_input = upfirdn2d_op.upfirdn2d(  # type: ignore[union-attr]
            grad_output,
            grad_kernel,
            down_x,
            down_y,
            up_x,
            up_y,
            g_pad_x0,
            g_pad_x1,
            g_pad_y0,
            g_pad_y1,
        )
        grad_input = grad_input.view(in_size[0], in_size[1], in_size[2], in_size[3])

        ctx.save_for_backward(kernel)

        pad_x0, pad_x1, pad_y0, pad_y1 = pad
        ctx.up_x = up_x
        ctx.up_y = up_y
        ctx.down_x = down_x
        ctx.down_y = down_y
        ctx.pad_x0 = pad_x0
        ctx.pad_x1 = pad_x1
        ctx.pad_y0 = pad_y0
        ctx.pad_y1 = pad_y1
        ctx.in_size = in_size
        ctx.out_size = out_size

        return grad_input

    @staticmethod
    def backward(ctx, gradgrad_input):
        (kernel,) = ctx.saved_tensors
        gradgrad_input = gradgrad_input.reshape(-1, ctx.in_size[2], ctx.in_size[3], 1)

        gradgrad_out = upfirdn2d_op.upfirdn2d(  # type: ignore[union-attr]
            gradgrad_input,
            kernel,
            ctx.up_x,
            ctx.up_y,
            ctx.down_x,
            ctx.down_y,
            ctx.pad_x0,
            ctx.pad_x1,
            ctx.pad_y0,
            ctx.pad_y1,
        )
        gradgrad_out = gradgrad_out.view(ctx.in_size[0], ctx.in_size[1], ctx.out_size[0], ctx.out_size[1])
        return gradgrad_out, None, None, None, None, None, None, None, None


class UpFirDn2d(Function):
    @staticmethod
    def forward(ctx, input, kernel, up, down, pad):
        up_x, up_y = up
        down_x, down_y = down
        pad_x0, pad_x1, pad_y0, pad_y1 = pad

        kernel_h, kernel_w = kernel.shape
        batch, channel, in_h, in_w = input.shape
        ctx.in_size = input.shape

        input = input.reshape(-1, in_h, in_w, 1)
        ctx.save_for_backward(kernel, torch.flip(kernel, [0, 1]))

        out_h = (in_h * up_y + pad_y0 + pad_y1 - kernel_h) // down_y + 1
        out_w = (in_w * up_x + pad_x0 + pad_x1 - kernel_w) // down_x + 1
        ctx.out_size = (out_h, out_w)

        ctx.up = (up_x, up_y)
        ctx.down = (down_x, down_y)
        ctx.pad = (pad_x0, pad_x1, pad_y0, pad_y1)

        g_pad_x0 = kernel_w - pad_x0 - 1
        g_pad_y0 = kernel_h - pad_y0 - 1
        g_pad_x1 = in_w * up_x - out_w * down_x + pad_x0 - up_x + 1
        g_pad_y1 = in_h * up_y - out_h * down_y + pad_y0 - up_y + 1
        ctx.g_pad = (g_pad_x0, g_pad_x1, g_pad_y0, g_pad_y1)

        out = upfirdn2d_op.upfirdn2d(  # type: ignore[union-attr]
            input, kernel, up_x, up_y, down_x, down_y, pad_x0, pad_x1, pad_y0, pad_y1
        )
        out = out.view(-1, channel, out_h, out_w)
        return out

    @staticmethod
    def backward(ctx, grad_output):
        kernel, grad_kernel = ctx.saved_tensors
        grad_input = UpFirDn2dBackward.apply(
            grad_output, kernel, grad_kernel, ctx.up, ctx.down, ctx.pad, ctx.g_pad, ctx.in_size, ctx.out_size
        )
        return grad_input, None, None, None, None


def upfirdn2d(input, kernel, up=1, down=1, pad=(0, 0), device="cpu"):
    if (
        UPFIRDN_AVAILABLE
        and platform.system() == "Linux"
        and torch.cuda.is_available()
        and device != "cpu"
    ):
        return UpFirDn2d.apply(input, kernel, (up, up), (down, down), (pad[0], pad[1], pad[0], pad[1]))

    # Native implementation works on both CPU and CUDA tensors.
    return upfirdn2d_native(input, kernel, up, up, down, down, pad[0], pad[1], pad[0], pad[1])


def upfirdn2d_native(input, kernel, up_x, up_y, down_x, down_y, pad_x0, pad_x1, pad_y0, pad_y1):
    input = input.permute(0, 2, 3, 1)
    _, in_h, in_w, minor = input.shape
    kernel_h, kernel_w = kernel.shape
    out = input.view(-1, in_h, 1, in_w, 1, minor)
    out = F.pad(out, [0, 0, 0, up_x - 1, 0, 0, 0, up_y - 1])
    out = out.view(-1, in_h * up_y, in_w * up_x, minor)

    out = F.pad(
        out, [0, 0, max(pad_x0, 0), max(pad_x1, 0), max(pad_y0, 0), max(pad_y1, 0)]
    )
    out = out[
        :,
        max(-pad_y0, 0) : out.shape[1] - max(-pad_y1, 0),
        max(-pad_x0, 0) : out.shape[2] - max(-pad_x1, 0),
        :,
    ]

    out = out.permute(0, 3, 1, 2)
    out = out.reshape([-1, 1, in_h * up_y + pad_y0 + pad_y1, in_w * up_x + pad_x0 + pad_x1])
    w = torch.flip(kernel, [0, 1]).view(1, 1, kernel_h, kernel_w)
    out = F.conv2d(out, w)
    out = out.reshape(
        -1,
        minor,
        in_h * up_y + pad_y0 + pad_y1 - kernel_h + 1,
        in_w * up_x + pad_x0 + pad_x1 - kernel_w + 1,
    )
    return out[:, :, ::down_y, ::down_x]
PY

echo "PATCHED $FUSED and $UPFIR (backups with .bak_$ts)"
"""

sh(patch)

