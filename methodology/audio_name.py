dataset_path = "insert_your_path"

with os.scandir(dataset_path) as entries:
    persons = sorted([entry.name for entry in entries if entry.is_dir()])[:50] #Для FF++ нужны первые 50 id, т.к. в FF++ 1000 видео

def audio_name(i):
    '''
    Алгоритм для поиска названия аудиофайла исходя из номера видео.
    Рассчет на датасет VoxCeleb2 (аудио) и FaceForensics++ (видео).

    Принимает:
        i: int - Номер видео 
    Возвращает:
        clip_path, clip_name: tuple(string, string) - Путь до аудио, Имя аудио для дальнейшего сохранения файла фейка
            формата (video_name)_(clip_name)
    '''
    person = persons[i // 20]
    person_path = dataset_path + "/" + person
    
    current_num = i % 20 // 5
    with os.scandir(person_path) as entries:
        current_clip = sorted([entry.name for entry in entries if entry.is_dir()])[current_num]

    clip_num = sorted([f for f in os.listdir(person_path + "/" + current_clip) 
                if os.path.isfile(os.path.join(person_path + "/" + current_clip, f))])[0]

    clip_path = person_path + "/" + current_clip + "/" + clip_num
    clip_name = person + "_" + current_clip + "_" + clip_num[:-4]

    # print(clip_path, clip_name)
    return clip_path, clip_name