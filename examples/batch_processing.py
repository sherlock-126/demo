#!/usr/bin/env python3
"""
Batch processing example for the content generator
"""

import os
import time
from dotenv import load_dotenv
from content_generator import ScriptGenerator

# Load environment variables
load_dotenv()

# List of parenting topics to process
TOPICS = [
    "Cách dạy con tự lập từ nhỏ",
    "Xử lý khi con không chịu ngủ",
    "Dạy con chia sẻ với bạn bè",
    "Cách phản ứng khi con nói dối",
    "Giúp con vượt qua nỗi sợ bóng tối"
]


def main():
    """Batch processing example"""

    print("Batch Processing Example")
    print("=" * 60)
    print(f"Processing {len(TOPICS)} topics...")
    print()

    # Initialize generator
    generator = ScriptGenerator()

    # Method 1: Using built-in batch processing
    print("Method 1: Built-in batch processing")
    print("-" * 40)

    results = generator.generate_batch(
        topics=TOPICS[:3],  # Process first 3 topics
        num_slides=4,
        language="vi"
    )

    # Display results
    for result in results:
        if result["status"] == "success":
            script = result["script"]
            print(f"✓ {script.topic}")
            print(f"  Title: {script.main_title}")
            print(f"  Slides: {len(script.slides)}")
        else:
            print(f"✗ {result['topic']}")
            print(f"  Error: {result['error']}")
        print()

    # Method 2: Manual batch processing with progress tracking
    print("Method 2: Manual batch with progress tracking")
    print("-" * 40)

    successful = []
    failed = []

    for i, topic in enumerate(TOPICS[3:], 1):  # Process remaining topics
        print(f"Processing {i}/{len(TOPICS[3:])}:", end=" ")

        try:
            script = generator.generate(
                topic=topic,
                num_slides=3,
                language="vi"
            )
            successful.append({
                "topic": topic,
                "title": script.main_title,
                "slides": len(script.slides)
            })
            print(f"✓ {topic[:30]}...")

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            failed.append({
                "topic": topic,
                "error": str(e)
            })
            print(f"✗ {topic[:30]}... ({e})")

    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total topics processed: {len(TOPICS)}")
    print(f"Successful: {len(successful) + sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {len(failed) + sum(1 for r in results if r['status'] == 'error')}")
    print()

    # List all generated scripts
    print("Generated Scripts:")
    all_scripts = generator.list_scripts(limit=20)
    for script in all_scripts[:10]:  # Show first 10
        print(f"  - {script['filename']}")
        print(f"    Topic: {script['topic'][:50]}...")
        print(f"    Slides: {script['num_slides']}")


def save_topics_to_file(filename="topics.txt"):
    """Save topics to a file for CLI batch processing"""
    with open(filename, "w", encoding="utf-8") as f:
        for topic in TOPICS:
            f.write(topic + "\n")
    print(f"Topics saved to {filename}")
    print("You can now run: python -m content_generator batch topics.txt")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your API key")
        exit(1)

    try:
        main()
        print("\n" + "-" * 60)
        save_topics_to_file()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)