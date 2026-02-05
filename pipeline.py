import json
from transformer import create_transformation_context, load_story_data, load_world_data
from prompts import (
    get_character_prompt, 
    get_conflict_prompt,
    get_assembly_prompt,
    VALIDATION_PROMPT
)
from llm_client import generate_structured, generate_creative, generate_text


class StoryTransformationPipeline:
    
    def __init__(self, story_key, world_key, verbose=True):
        self.story_key = story_key
        self.world_key = world_key
        self.verbose = verbose
        
        self.context = None
        self.transformed_characters = []
        self.transformed_conflict = None
        self.final_story = None
        self.validation_result = None
    
    def log(self, message):
        if self.verbose:
            print(f"[Pipeline] {message}")
    
    def step1_build_context(self):
        self.log("Building transformation context...")
        self.context = create_transformation_context(self.story_key, self.world_key)
        self.log(f"  Source: {self.context['source_story']['title']}")
        self.log(f"  Target: {self.context['target_world']['name']}")
        return self.context
    
    def step2_transform_characters(self):
        self.log("Transforming characters...")
        
        system_msg = (
            "You are a creative writing assistant specializing in story adaptation. "
            "You understand that characters must keep their NARRATIVE FUNCTION while "
            "changing their surface details to fit new worlds."
        )
        
        for char_mapping in self.context['character_mappings']:
            self.log(f"  Transforming {char_mapping['original_name']}...")
            
            prompt = get_character_prompt(char_mapping)
            result = generate_structured(prompt, system_msg)
            
            self.transformed_characters.append({
                'original': char_mapping['original_name'],
                'transformation': result
            })
        
        self.log(f"  Transformed {len(self.transformed_characters)} characters")
        return self.transformed_characters
    
    def step3_transform_conflict(self):
        self.log("Transforming central conflict...")
        
        system_msg = (
            "You are analyzing story structure. The conflict must create the same "
            "EMOTIONAL STAKES while using completely different surface elements."
        )
        
        prompt = get_conflict_prompt(
            self.context['conflict_mapping'],
            self.context['target_world']['name']
        )
        
        self.transformed_conflict = generate_structured(prompt, system_msg)
        self.log("  Conflict transformed")
        return self.transformed_conflict
    
    def step4_generate_story(self):
        self.log("Generating full story...")
        
        char_summaries = "\n\n".join([
            f"**{c['original']}** becomes:\n{c['transformation']}"
            for c in self.transformed_characters
        ])
        
        scene_summaries = "\n".join([
            f"- {beat['original_beat']}" 
            for beat in self.context['plot_structure']
        ])
        
        prompt = get_assembly_prompt(
            source_info={
                'title': self.context['source_story']['title'],
                'themes': self.context['source_story']['themes'],
                'emotional_core': self.context['source_story']['emotional_core']
            },
            world_info=self.context['target_world'],
            characters=char_summaries,
            conflict=self.transformed_conflict,
            scenes=scene_summaries
        )
        
        system_msg = (
            "You are a skilled fiction writer. Write vivid, engaging prose that "
            "brings this reimagined story to life. Use sensory details and natural "
            "dialogue. The story should feel fresh while honoring its source."
        )
        
        self.final_story = generate_creative(prompt, system_msg)
        self.log("  Story generated")
        return self.final_story
    
    def step5_validate(self):
        self.log("Validating thematic fidelity...")
        
        prompt = VALIDATION_PROMPT.format(
            original_themes=', '.join(self.context['source_story']['themes']),
            emotional_core=self.context['source_story']['emotional_core'],
            story_text=self.final_story
        )
        
        self.validation_result = generate_structured(prompt)
        self.log("  Validation complete")
        return self.validation_result
    
    def run(self):
        self.log("Starting Story Transformation Pipeline")
        
        self.step1_build_context()
        self.step2_transform_characters()
        self.step3_transform_conflict()
        self.step4_generate_story()
        self.step5_validate()
        
        self.log("Pipeline complete!")
        
        return self.get_full_output()
    
    def get_full_output(self):
        return {
            'metadata': {
                'source': self.context['source_story']['title'],
                'target_world': self.context['target_world']['name'],
                'themes_preserved': self.context['source_story']['themes']
            },
            'transformation_details': {
                'characters': self.transformed_characters,
                'conflict': self.transformed_conflict
            },
            'story': self.final_story,
            'validation': self.validation_result
        }


def save_output(result, filename="output.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved to {filename}")


def print_story_only(result):
    print("REIMAGINED STORY")
    print(f"\nOriginal: {result['metadata']['source']}")
    print(f"New Setting: {result['metadata']['target_world']}")
    print(result['story'])


if __name__ == "__main__":
    pipeline = StoryTransformationPipeline(
        story_key="romeo_and_juliet",
        world_key="silicon_valley_tech"
    )
    result = pipeline.run()
    print_story_only(result)
    save_output(result)
