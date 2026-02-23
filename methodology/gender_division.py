import os
import cv2
import pandas as pd
from deepface import DeepFace
from pathlib import Path

class SimpleGenderAnalyzer:
    def __init__(self, video_folder="./videos/", output_csv="gender_results.csv"):
        self.video_folder = video_folder
        self.output_csv = output_csv
        
    def extract_key_frame(self, video_path):
        """Extract the most clear face frame from video"""
        cap = cv2.VideoCapture(video_path)
        best_frame = None
        best_face_score = 0
        
        # Try different points in the video
        frame_positions = [0.1, 0.3, 0.5, 0.7, 0.9]  # Sample at 10%, 30%, etc.
        
        for pos in frame_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * pos))
            ret, frame = cap.read()
            if ret:
                # Use DeepFace's built-in face detection to find best frame
                try:
                    analysis = DeepFace.analyze(
                        frame, 
                        actions=['gender'], 
                        detector_backend='retinaface',  # Best accuracy
                        enforce_detection=True,
                        silent=True
                    )
                    # Use confidence as quality score
                    confidence = analysis[0]['gender'][analysis[0]['dominant_gender']]
                    if confidence > best_face_score:
                        best_face_score = confidence
                        best_frame = frame
                except:
                    continue
        
        cap.release()
        return best_frame
    
    def analyze_all_videos(self):
        """Analyze videos 000.mp4 to 999.mp4"""
        results = []
        
        for i in range(1000):
            video_name = f"{i:03d}.mp4"
            video_path = os.path.join(self.video_folder, video_name)
            
            if not os.path.exists(video_path):
                print(f"⚠️  {video_name} not found, skipping...")
                results.append({"video": video_name, "gender": "not_found", "confidence": 0})
                continue
            
            print(f"🔍 Processing {video_name}...")
            
            try:
                # Method 1: Try analyzing directly from video file (faster)
                analysis = DeepFace.analyze(
                    video_path,
                    actions=['gender'],
                    detector_backend='retinaface',
                    enforce_detection=False,
                    silent=True
                )
                
                gender = analysis[0]['dominant_gender']
                confidence = analysis[0]['gender'][gender]
                
            except:
                # Method 2: Extract frame and analyze
                try:
                    frame = self.extract_key_frame(video_path)
                    if frame is not None:
                        analysis = DeepFace.analyze(
                            frame, 
                            actions=['gender'], 
                            detector_backend='retinaface',
                            enforce_detection=True,
                            silent=True
                        )
                        gender = analysis[0]['dominant_gender']
                        confidence = analysis[0]['gender'][gender]
                    else:
                        gender = "unknown"
                        confidence = 0
                except:
                    gender = "error"
                    confidence = 0
            
            results.append({
                "video": video_name,
                "gender": gender,
                "confidence": float(confidence),
                "male_score": analysis[0]['gender']['Man'] if 'analysis' in locals() else 0,
                "female_score": analysis[0]['gender']['Woman'] if 'analysis' in locals() else 0
            })
            
            print(f"   → Result: {gender} ({confidence:.1f}%)")
        
        # Save to CSV
        df = pd.DataFrame(results)
        df.to_csv(self.output_csv, index=False)
        print(f"\n✅ Analysis complete! Results saved to {self.output_csv}")
        print(f"   Total analyzed: {len([r for r in results if r['gender'] not in ['not_found', 'error', 'unknown']])}/1000")
        
        return df

# Run the analysis
if __name__ == "__main__":
    analyzer = SimpleGenderAnalyzer(
        video_folder="./videos/",  # Your folder with 000.mp4-999.mp4
        output_csv="gender_predictions.csv"
    )
    results_df = analyzer.analyze_all_videos()
    
    # Show summary statistics
    summary = results_df['gender'].value_counts()
    print("\n📊 Summary:")
    for gender, count in summary.items():
        print(f"   {gender}: {count} videos")