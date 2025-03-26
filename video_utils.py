import os
from openai import OpenAI
import cv2
import base64
from io import BytesIO
import tiktoken


def extract_frames(video_file, interval=1.0):
    """
    Extract frames from the video at specified intervals and save them to video_images folder.

    Args:
        video_file: OpenCV VideoCapture object or path to video file
        interval (float): Time interval in seconds between frames to extract
    """
    # Create output directory if it doesn't exist
    output_dir = "video_images"
    os.makedirs(output_dir, exist_ok=True)

    # If video_file is a string (path), create VideoCapture object
    if isinstance(video_file, str):
        video_file = cv2.VideoCapture(video_file)

    if not video_file.isOpened():
        print("Error: Could not open video file")
        return

    # Get video properties
    fps = video_file.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    frame_count = 0
    saved_count = 0

    try:
        while True:
            ret, frame = video_file.read()
            if not ret:
                break

            # Save frame at specified intervals
            if frame_count % frame_interval == 0:
                frame_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                saved_count += 1

            frame_count += 1

    finally:
        video_file.release()
        print(f"Extracted {saved_count} frames to {output_dir}/")


def transcribe_video(video_file):
    """
    Transcribe the video file using OpenAI's Whisper model.

    Args:
        video_file: File object or path to video file
    """
    # Initialize OpenAI client
    client = OpenAI()

    try:
        # If video_file is a string (path), open the file
        if isinstance(video_file, str):
            video_file = open(video_file, "rb")

        # Create transcription with timestamps
        transcript = client.audio.transcriptions.create(
            file=video_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

        # Print the transcription with timestamps
        for segment in transcript.segments:
            start_time = segment.start
            end_time = segment.end
            text = segment.text
            print(f"[{start_time:.2f}s - {end_time:.2f}s] {text}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the file if we opened it
        if isinstance(video_file, str):
            video_file.close()


def get_video_moments_text_and_images(video_file, interval=1.0):
    """
    Process a video file to extract frames and transcriptions, returning them in a unified format.

    Args:
        video_file: Path to video file, VideoCapture object, or file object
        interval (float): Time interval in seconds between frames to extract

    Returns:
        list: List of dictionaries containing either image or transcription data
    """
    # Initialize OpenAI client for transcription
    client = OpenAI()

    # Handle different input types
    if isinstance(video_file, str):
        # If it's a path, use it directly
        video_path = video_file
        cap = cv2.VideoCapture(video_path)
    elif isinstance(video_file, cv2.VideoCapture):
        # If it's already a VideoCapture object
        cap = video_file
        video_path = None
    else:
        # If it's a file object, we need to get the path
        video_path = video_file.name
        cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError("Could not open video file")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    frame_count = 0
    moments = []

    try:
        # First, get the transcription
        if video_path:
            # If we have a path, use it directly
            with open(video_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )
        else:
            # If we have a VideoCapture object, we need to extract audio in memory
            # First, capture all frames to memory
            frames = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)

            # Create in-memory video file
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            height, width = frames[0].shape[:2]

            # Create a buffer to hold the video data
            buffer = BytesIO()

            # Create a temporary video writer that writes to memory
            temp_video_path = (
                "temp_video.mp4"  # This is just for the writer initialization
            )
            out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

            # Write frames to the video writer
            for frame in frames:
                out.write(frame)
            out.release()

            # Read the temporary file into memory and delete it
            with open(temp_video_path, "rb") as f:
                buffer = BytesIO(f.read())
            os.remove(temp_video_path)

            # Use the in-memory buffer for transcription
            buffer.seek(0)
            transcript = client.audio.transcriptions.create(
                file=buffer,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        # Add transcriptions to moments
        for segment in transcript.segments:
            moments.append(
                {
                    "type": "transcription",
                    "start_time": segment.start,
                    "end_time": segment.end,
                    "content": segment.text,
                }
            )

        # Reset video capture to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Process frames
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                # Calculate start and end times for this frame
                start_time = frame_count / fps
                end_time = (frame_count + frame_interval) / fps

                # Convert frame to base64
                _, buffer = cv2.imencode(".jpg", frame)
                img_str = base64.b64encode(buffer).decode("utf-8")

                moments.append(
                    {
                        "type": "image",
                        "start_time": start_time,
                        "end_time": end_time,
                        "content": img_str,
                    }
                )

            frame_count += 1

    finally:
        if cap != video_file:  # Only release if we created the capture object
            cap.release()

    # Sort moments by start time and type (image before transcription when times are equal)
    return sorted(
        moments,
        key=lambda x: (
            x.get("start_time", 0),
            0 if x["type"] == "image" else 1,  # 0 for image, 1 for transcription
        ),
    )


def count_tokens_in_messages(messages, model="gpt-4o"):
    """
    Count the number of tokens in a list of messages, handling both text and image messages.

    Args:
        messages (list): List of message dictionaries
        model (str): Model name to use for token encoding

    Returns:
        int: Total number of tokens in the messages
    """
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0

    for message in messages:
        if isinstance(message["content"], list):
            # For messages with images, count only the text part
            for content in message["content"]:
                if content["type"] == "text":
                    total_tokens += len(encoding.encode(content["text"]))
        else:
            # For regular text messages
            total_tokens += len(encoding.encode(message["content"]))

    return total_tokens


def get_full_video_description_with_dialogues(video_file, interval=10):
    """
    Get a detailed description of the video content using GPT-4 Turbo Vision, including both visual elements and dialogues.

    Args:
        video_file: Path to video file, VideoCapture object, or file object
        interval (float): Time interval in seconds between frames to extract

    Returns:
        str: A detailed description of the video content
    """
    # Get video moments (frames and transcriptions)
    moments = get_video_moments_text_and_images(video_file, interval)

    # Initialize OpenAI client
    client = OpenAI()

    # Prepare messages for GPT-4 Turbo Vision
    messages = [
        {
            "role": "system",
            "content": "You are a video content analyzer. Your task is to describe what's happening in the video, "
            "combining both visual elements and dialogues to create a coherent narrative. "
            "Focus on describing the scene, actions, and how they relate to the spoken content.",
        }
    ]

    # Process each moment in sequence
    for moment in moments:
        if moment["type"] == "image":
            # Add image content with proper base64 format
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"At {moment['start_time']:.1f} seconds into the video, here's what the scene looks like:",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{moment['content']}"
                            },
                        },
                    ],
                }
            )
        else:  # transcription
            # Add transcription content
            messages.append(
                {
                    "role": "user",
                    "content": f"At {moment['start_time']:.1f} seconds, someone says: {moment['content']}",
                }
            )

    # Add final prompt to get the description
    messages.append(
        {
            "role": "user",
            "content": "Please provide a detailed description of what's happening in this video, "
            "combining both the visual elements and dialogues to create a coherent narrative.",
        }
    )

    # Count and print tokens
    total_tokens = count_tokens_in_messages(messages)
    print(f"Total tokens in messages: {total_tokens}")

    try:
        # Call GPT-4 Turbo Vision API with updated parameters
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,  # Added temperature for more natural responses
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred while analyzing the video: {str(e)}")
        return None
