import json
from pathlib import Path


def load_story_data(story_key):
    data_path = Path(__file__).parent / "data" / "stories.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        stories = json.load(f)
    
    if story_key not in stories:
        available = list(stories.keys())
        raise ValueError(f"Story '{story_key}' not found. Available: {available}")
    
    return stories[story_key]


def load_world_data(world_key):
    data_path = Path(__file__).parent / "data" / "worlds.json"
    with open(data_path, 'r', encoding='utf-8') as f:
        worlds = json.load(f)
    
    if world_key not in worlds:
        available = list(worlds.keys())
        raise ValueError(f"World '{world_key}' not found. Available: {available}")
    
    return worlds[world_key]


def map_character_to_world(character, world_data):
    role = character['role']
    traits = character['traits']
    
    role_mappings = {
        'protagonist': world_data['social_hierarchy'][1:3],  
        'antagonist': world_data['power_structures'][:2],   
        'catalyst': world_data['social_hierarchy'][2:4],    
        'helper': world_data['power_structures'][2:],       
        'victim': world_data['social_hierarchy'][-2:],     
        'mentor': world_data['power_structures'][1:3],   
    }
    
    suggested_positions = role_mappings.get(role, world_data['social_hierarchy'])
    
    return {
        'original_name': character['name'],
        'original_role': role,
        'original_traits': traits,
        'original_arc': character['arc'],
        'suggested_new_positions': suggested_positions,
        'world_context': world_data['name']
    }


def map_conflict_to_world(original_conflict, world_data):
    world_conflicts = world_data['conflicts']
    world_values = world_data['values']
    world_taboos = world_data['taboos']
    
    return {
        'original_conflict': original_conflict,
        'available_world_conflicts': world_conflicts,
        'world_values_to_leverage': world_values,
        'world_taboos_to_violate': world_taboos, 
    }


def map_plot_beats_to_world(plot_beats, world_data):
    mapped_beats = []
    
    for beat in plot_beats:
        mapped_beats.append({
            'original_beat': beat,
            'communication_methods': world_data['communication'],
            'power_structures': world_data['power_structures'],
            'setting_aesthetic': world_data['aesthetic']
        })
    
    return mapped_beats


def create_transformation_context(story_key, world_key):
    story = load_story_data(story_key)
    world = load_world_data(world_key)
    
    character_mappings = []
    for char in story['key_characters']:
        mapping = map_character_to_world(char, world)
        character_mappings.append(mapping)
    
    conflict_mapping = map_conflict_to_world(story['central_conflict'], world)
    
    plot_mapping = map_plot_beats_to_world(story['plot_beats'], world)
    
    return {
        'source_story': {
            'title': story['title'],
            'author': story['author'],
            'original_era': story['era'],
            'themes': story['core_themes'],
            'emotional_core': story['emotional_core']
        },
        'target_world': {
            'name': world['name'],
            'era': world['era'],
            'setting': world['setting'],
            'aesthetic': world['aesthetic'],
            'technology': world['technology_level']
        },
        'character_mappings': character_mappings,
        'conflict_mapping': conflict_mapping,
        'plot_structure': plot_mapping,
        'preservation_requirements': [
            f"MUST preserve theme: {theme}" for theme in story['core_themes']
        ] + [
            f"MUST preserve emotional core: {story['emotional_core']}"
        ]
    }

if __name__ == "__main__":
    ctx = create_transformation_context("romeo_and_juliet", "silicon_valley_tech")
    print(json.dumps(ctx, indent=2))
