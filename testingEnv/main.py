import logging
import os
import whisper
import subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# File paths
inputDir = "src"
outputDir = "output"
srtDir = "srt"

# Loading Model
model = whisper.load_model("small")

# Ensure output directories exist
os.makedirs(inputDir, exist_ok=True)
os.makedirs(outputDir, exist_ok=True)
os.makedirs(srtDir, exist_ok=True)

class SRTgen:
    def __init__(self, fileName) -> None:
        self.inputPath = os.path.join(os.getcwd(), inputDir, fileName + '.mp4')
        self.outputPath = os.path.join(os.getcwd(), outputDir, fileName + '.mp3')
        self.srtPath = os.path.join(os.getcwd(), srtDir, fileName + ".srt")
    
    def extractAudioFromVideo(self):
        '''Extracting Audio (mp3) from the video file'''
        try:
            print(f"Extracting audio from {self.inputPath} to {self.outputPath}")
            command = [
                'ffmpeg',
                '-i', self.inputPath,
                '-q:a', '0',
                '-map', 'a',
                self.outputPath
            ]
            subprocess.run(command, check=True)
            if os.path.exists(self.outputPath):
                print(f"Audio file created successfully at {self.outputPath}")
            else:
                print(f"Failed to create audio file at {self.outputPath}")
        except Exception as error:
            logging.error(f"Error: {error}")

    def generate(self):
        '''This will generate the srt file from mp4'''
        self.extractAudioFromVideo()
        if not os.path.exists(self.outputPath):
            logging.error(f"Audio file does not exist at {self.outputPath}. Please check the extraction process.")
            return

        result = model.transcribe(self.outputPath)
        self.segments = result['segments']
        self.output = []
        
        for i, sentence in enumerate(self.segments):
            start_time = sentence['start']
            end_time = sentence['end']
            text = sentence['text'].strip()
            
            if text:  # Only write non-empty sentences
                self.output.append(
                    {
                        'index': i + 1,
                        'startTime': start_time,
                        'endTime': end_time,
                        'text': text
                    }
                )
        
        self.write_SRT()

    def convert_to_srt_time(self, seconds):
        '''Convert seconds to SRT time format (hours:minutes:seconds,milliseconds).'''
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def write_SRT(self):
        '''Writing SRT File from output list'''
        with open(self.srtPath, 'w') as file:
            for entry in self.output:
                start_time = self.convert_to_srt_time(entry['startTime'])
                end_time = self.convert_to_srt_time(entry['endTime'])
                file.write(f"{entry['index']}\n")
                file.write(f"{start_time} --> {end_time}\n")
                file.write(f"{entry['text']}\n\n")
