CHARACTER_TRANSFORM_PROMPT = """You are helping adapt a classic story to a new setting.

ORIGINAL CHARACTER:
- Name: {original_name}
- Role in story: {original_role}  
- Key traits: {original_traits}
- Character arc: {original_arc}

TARGET WORLD: {world_context}
Suggested positions in this world: {suggested_positions}

Your task: Create a new version of this character that:
1. Keeps their role in the story (they must still be the {original_role})
2. Keeps their core traits ({original_traits}) but expressed through this world's lens
3. Keeps their arc ({original_arc}) but using this world's circumstances
4. Fits naturally into {world_context}

Respond with:
- New name (fitting the world)
- New position/job in this world
- How their traits manifest in this setting
- Their backstory (2-3 sentences)
- Key relationships they'd have

Be specific to {world_context}. No generic answers."""


CONFLICT_TRANSFORM_PROMPT = """You are adapting a story's central conflict to a new world.

ORIGINAL CONFLICT: {original_conflict}

TARGET WORLD CONTEXT:
- Setting: {world_name}
- Available conflict types: {world_conflicts}
- Values people care about: {world_values}
- Taboos that create tension: {world_taboos}

Your task: Reframe the original conflict for this world.

The conflict must:
1. Create the SAME emotional stakes as the original
2. Use this world's specific power dynamics
3. Feel inevitable within this world's logic
4. Lead to similar consequences

Describe:
- The new conflict (1 paragraph)
- Why it matters in this world
- What makes it hard to resolve
- The stakes for each side"""

SCENE_PROMPT = """You are writing a scene for an adapted story.

STORY CONTEXT:
- Original work: {source_title} by {source_author}
- Theme we must preserve: {theme}
- Emotional core: {emotional_core}

SCENE REQUIREMENTS:
- Plot beat to hit: {plot_beat}
- Setting: {world_setting}
- Available communication methods: {communication}
- Visual aesthetic: {aesthetic}

CHARACTERS IN SCENE:
{characters_in_scene}

Write this scene (300-400 words):
- Start in the middle of action
- Use dialogue that sounds natural for {world_setting}
- Show don't tell the emotional stakes
- End with a hook to the next beat

Write in present tense, third person limited."""

STORY_ASSEMBLY_PROMPT = """You are assembling a complete reimagined story.

TRANSFORMATION SUMMARY:
Original: {source_title}
New Setting: {world_name}
Core theme preserved: {themes}
Emotional core: {emotional_core}

CHARACTERS (already transformed):
{character_summaries}

CONFLICT (already transformed):
{conflict_summary}

SCENE OUTLINES:
{scene_summaries}

Now write the complete story (600-1000 words) that:
1. Flows naturally between the scenes above
2. Maintains consistent character voices
3. Builds to the emotional climax
4. Ends with thematic resonance matching the original

Use the world's aesthetic throughout: {aesthetic}

Write in a literary style appropriate for {world_name}."""


VALIDATION_PROMPT = """Review this transformed story for thematic fidelity.

ORIGINAL THEMES: {original_themes}
ORIGINAL EMOTIONAL CORE: {emotional_core}

TRANSFORMED STORY:
{story_text}

Check:
1. Is each original theme present? (list which are present/missing)
2. Does the emotional core come through? (yes/no with explanation)
3. Are there any elements that contradict the original's message?
4. Rate thematic fidelity 1-10

Be specific and critical."""


def get_character_prompt(character_mapping):
    """Enter the character transformation prompt"""
    return CHARACTER_TRANSFORM_PROMPT.format(
        original_name=character_mapping['original_name'],
        original_role=character_mapping['original_role'],
        original_traits=', '.join(character_mapping['original_traits']),
        original_arc=character_mapping['original_arc'],
        world_context=character_mapping['world_context'],
        suggested_positions=', '.join(character_mapping['suggested_new_positions'])
    )


def get_conflict_prompt(conflict_mapping, world_name):
    """Enter the conflict transformation prompt"""
    return CONFLICT_TRANSFORM_PROMPT.format(
        original_conflict=conflict_mapping['original_conflict'],
        world_name=world_name,
        world_conflicts=', '.join(conflict_mapping['available_world_conflicts']),
        world_values=', '.join(conflict_mapping['world_values_to_leverage']),
        world_taboos=', '.join(conflict_mapping['world_taboos_to_violate'])
    )


def get_scene_prompt(plot_beat_mapping, source_info, theme, characters_text):
    """Enter a scene generation prompt"""
    return SCENE_PROMPT.format(
        source_title=source_info['title'],
        source_author=source_info['author'],
        theme=theme,
        emotional_core=source_info['emotional_core'],
        plot_beat=plot_beat_mapping['original_beat'],
        world_setting=source_info.get('target_setting', 'the new world'),
        communication=', '.join(plot_beat_mapping['communication_methods']),
        aesthetic=plot_beat_mapping['setting_aesthetic'],
        characters_in_scene=characters_text
    )


def get_assembly_prompt(source_info, world_info, characters, conflict, scenes):
    """Enter the final assembly prompt"""
    return STORY_ASSEMBLY_PROMPT.format(
        source_title=source_info['title'],
        world_name=world_info['name'],
        themes=', '.join(source_info['themes']),
        emotional_core=source_info['emotional_core'],
        character_summaries=characters,
        conflict_summary=conflict,
        scene_summaries=scenes,
        aesthetic=world_info['aesthetic']
    )
