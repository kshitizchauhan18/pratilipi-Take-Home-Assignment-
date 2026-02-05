#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline import StoryTransformationPipeline, save_output, print_story_only
from transformer import load_story_data, load_world_data


def list_options():
    stories_path = Path(__file__).parent / "data" / "stories.json"
    with open(stories_path, 'r', encoding='utf-8') as f:
        stories = json.load(f)
    
    worlds_path = Path(__file__).parent / "data" / "worlds.json"
    with open(worlds_path, 'r', encoding='utf-8') as f:
        worlds = json.load(f)
    
    print("AVAILABLE SOURCE STORIES")
    for key, story in stories.items():
        print(f"\n  {key}")
        print(f"    Title: {story['title']}")
        print(f"    Author: {story['author']}")
        print(f"    Themes: {', '.join(story['core_themes'][:2])}...")
    
    print("\n AVAILABLE TARGET WORLDS")
    for key, world in worlds.items():
        print(f"\n  {key}")
        print(f"    Setting: {world['name']}")
        print(f"    Era: {world['era']}")
        print(f"    Aesthetic: {world['aesthetic'][:50]}...")
    
    print("\n")


def interactive_mode():
    print("STORY TRANSFORMATION SYSTEM")
    print("\nThis system transforms classic stories into new settings")
    print("while preserving their emotional core.\n")
    
    list_options()
    
    print("-" * 50)
    story = input("Enter story key (e.g., romeo_and_juliet): ").strip()
    world = input("Enter world key (e.g., silicon_valley_tech): ").strip()
    
    if not story or not world:
        print("Error: Both story and world are required")
        return None
    
    return story, world


def format_output_markdown(result):
    md = []
    
    md.append(f"# {result['metadata']['source']} — Reimagined\n")
    md.append(f"Original:** {result['metadata']['source']}")
    md.append(f"New Setting:** {result['metadata']['target_world']}")
    md.append(f"Core Themes:** {', '.join(result['metadata']['themes_preserved'])}\n")
    
    md.append("---\n")
    
    md.append("## The Reimagined Story\n")
    md.append(result['story'])
    
    md.append("\n\n---\n")
    
    md.append("Transformation Notes\n")
    md.append("Key decisions made during the adaptation process:*\n")
    
    md.append("Character Adaptations\n")
    for char in result['transformation_details']['characters']:
        md.append(f"**{char['original']}:** ")
        lines = char['transformation'].strip().split('\n')
        summary = ' '.join(lines[:3]).strip()
        if len(summary) > 200:
            summary = summary[:200] + "..."
        md.append(f"{summary}\n")
    
    md.append("\n Conflict Reimagined\n")
    conflict_summary = result['transformation_details']['conflict'].strip().split('\n\n')[0]
    md.append(conflict_summary)
    
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Transform classic stories into new settings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py --list
    python run.py --story romeo_and_juliet --world silicon_valley_tech
    python run.py --story hamlet --world cyberpunk_megacity
    python run.py --story odyssey --world space_colony
        """
    )
    
    parser.add_argument('--story', type=str, help='Source story key')
    parser.add_argument('--world', type=str, help='Target world key')
    parser.add_argument('--list', action='store_true', help='List available options')
    parser.add_argument('--output', type=str, default='output', help='Output filename (without extension)')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')
    
    args = parser.parse_args()
    
    if args.list:
        list_options()
        return
    
    if not args.story or not args.world:
        result = interactive_mode()
        if result is None:
            return
        story_key, world_key = result
    else:
        story_key = args.story
        world_key = args.world
    
    try:
        load_story_data(story_key)
        load_world_data(world_key)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nUse --list to see available options")
        return
    
    print(f"\nTransforming '{story_key}' into '{world_key}' setting...\n")
    
    pipeline = StoryTransformationPipeline(
        story_key=story_key,
        world_key=world_key,
        verbose=not args.quiet
    )
    
    try:
        result = pipeline.run()
    except Exception as e:
        print(f"\nError during transformation: {e}")
        print("Make sure GROQ_API_KEY environment variable is set")
        return
    
    json_file = f"{args.output}.json"
    md_file = f"{args.output}.md"
    
    save_output(result, json_file)
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(format_output_markdown(result))
    print(f"Saved markdown to {md_file}")
    
    print_story_only(result)


if __name__ == "__main__":
    main()
