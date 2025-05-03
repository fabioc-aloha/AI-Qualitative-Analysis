import os
from dotenv import load_dotenv
import openai
from pathlib import Path

def load_template():
    with open("AnalysisTemplate.txt", "r", encoding="utf-8") as f:
        return f.read()

def process_transcript(transcript_path, template):
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    
    # Prepare the prompt
    prompt = f"{template}\n\nTRANSCRIPT:\n{transcript}"
    
    try:
        response = openai.ChatCompletion.create(
            engine="YOUR_DEPLOYMENT_NAME",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing interview transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000  # Adjust based on your model
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing {transcript_path}: {str(e)}")
        return None

def main():
    # Load environment variables
    load_dotenv()
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-07-01-preview"
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")

    # Create reports directory if it doesn't exist
    Path("./reports").mkdir(exist_ok=True)
    
    # Load the analysis template
    template = load_template()
    
    # Process each transcript
    for transcript_file in Path("./transcripts").glob("*.txt"):
        print(f"Processing {transcript_file}")
        
        # Generate the output filename
        output_file = Path("./reports") / f"{transcript_file.stem}_analysis.md"
        
        # Process the transcript
        result = process_transcript(transcript_file, template)
        
        if result:
            # Save the result
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Saved analysis to {output_file}")

if __name__ == "__main__":
    main()