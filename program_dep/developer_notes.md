# Developer Notes
Documentation for adding new things.

## Commands
### Description
```
"""___category__<category>___category__
___parameters__`<parameter_name>` - <parameter_desc>___parameters__
___description__<desc>___description__
___duplicate__<duplicate?>___duplicate__"""
```
`category` - The category that the command belongs to. Must match a key in the category description .json file.</br>
`parameter_name` - Name of a parameter.<br/>
`parameter_desc` - Description of a parameter.<br/>
`desc` - The description of the command.<br/>
`duplicate?` - The original command, if there is one. If the command is a shorthand, alternative, etc. and is a duplicate, and therefore does not need to be documented in the help command, this parameter should be filled in, with anything, preferably the original command name. If there is no invocation, use `##none##`.<br/>

* The description is by default, in italics, wrapped with asterisks. To disable italics, wrap the description with backslashes.
* A list of available categories can be found at `program_dep/loc_other/command_category_description_database.json`.
* Fill in parameters and descriptions like plain Discord syntax. Start a new line for line breaks (this is a triple-quoted string).
* Treat the string block as a function docstring.
* Redirects, shorthands, alternatives or commands using the `ctx.invoke()` method do not need a docstring for descriptions. They will not be displayed in the help command.

### Categories
```
 "<category_name_formatted>": {
    "name": "<category_name_formatted>",
    "description": "<category_desc>",
    "emoji": "<emoji>"
  }
```
`category_name_formatted` - The category's name, formatted (capitalized, spaced correctly, etc).</br>
`category_desc` - Description of the category.<br/>
`emoji` - The emoji of the category. Use `<:emoji_name:emoji_id>` syntax.

* Use commas after each category (except the last one) like `json` syntax.
* The `name` field is not used currently, but please follow the rules to avoid breaking further changes.
* Make sure that the command's docstring's category field can match the key of this pair.
* Make the emoji an icon, preferably a small one (e.g. melee) of a weapon in PAYDAY 2.

### Developer-only commands
* Developer-only commands' names must start with an underscore, in order for it to not register in the help command.
* A decorator must be applied:
  ```
  @commands.is_owner()
  ```
  This ensures that no one but the owner of the bot is the only one able to run the command.
* Docstrings should be filled in as usual, to avoid changes in the future that may break.

## Databases
Most databases are located inside `program_dep`. Game databases are saved in the `loc_game` directory.

### Dealing with Classes and Objects
JSON files cannot store classes. To store a class, convert it to a json-readable string.

The class or object to be stored must have an attribute named `__storetype`, with a value of `"class"`.
```
json_readable_string = json.dumps(PythonObject.__dict__)
```
This is also available as a function in `savetools.py`, `class_to_json()`.
```
json_readable_string = class_to_json(PythonObject)
```

### mask.json
```
"<mask_id>": {
  "name": "<mask_name>",
  "images": {
    "default": "<default_url>",
    "<extra_id>": "<extra_url>"
  },
  "description": "<mask_desc>",
  "emoji": "<mask_emoji>"
}
```
`mask_id` - The ID of the mask, a string.
<br/>`mask_name` - The name of the mask, formatted.
<br/>`default_url` - The URL of the default mask image.
<br/>`extra_id` - Extra IDs of alternate mask images, if any.
<br/>`extra_url` - Extra URLs of alternate mask images, if any.
<br/>`mask_desc` - The description of the mask.
<br/>`mask_emoji` - The emoji of the mask.

### outfit.json
```
"<outfit_name>": {
  "name": "<outfit_name_formatted>",
  "description": "<outfit_description>",
  "image": "<outfit_image>",
  "variations": {
    "default": {
      "name": "<default_variation_name_formatted>",
      "image": "<default_variation_image>",
      "description": "<default_variation_description>"
    }
  }
}
```
`outfit_name` - The ID of the outfit, a string.
<br/>`outfit_name_formatted` - The name of the outfit, formatted.
<br/>`outfit_description` - The description of the outfit.
<br/>`outfit_image` - The image URL of the outfit (black and white). The coloured version would be the image of the first variation.
<br/>`default_variation_name_formatted` - The name of the default (and therefore, first) variation, formatted.
<br/>`default_variation_image` - The image URL of the default (and therefore, first) variation.
<br/>`default_variation_description` - The description of the default (and therefore, first) variation.

Extra variations can be added by the same syntax as the first/default variation. There must be a duplicate of the default variation, but with a different key:
```
"default": {"name": "Disturbing Violet", ...},
"disturbing_violet": {"name": "Disturbing Violet", ...},
"professor_white": {"name": "Professor White", ...},
```

### equipment.json
```
"<equipment_id>": {
  "name": "<name>",
  "image": "<image>",
  "description": "<description>"
}
```
`equipment_id` - The ID of the equipment, a string.
<br/>`name` - The name of the equipment, formatted.
<br/>`image` - The image URL of the equipment.
<br/>`description` - The description of the equipment.

New equipment is generally rare and this .json file shouldn't be updated very often.

### weapon_primary.json and weapon_secondary.json
Primary weapons and secondary weapons have a very complicated syntax. Important information will be added here - otherwise, simply copy a previous line and paste it below.

### throwable.json
```
"<id>": {
  "name": "<name>",
  "image": "<image>",
  "description": "<description>",
  "statistics": {
    "damage": <damage>,
    "capacity": <capacity>,
    "extra": {
      "<extra_field>": <extra_value>
    }
  },
  "lock": <lock>
}
```
`id` - The ID of the throwable.
<br/>`name` - The name of the throwable, formatted.
<br/>`image` - The image link of the throwable.
<br/>`description` - The description of the throwable.
<br/>`damage` - The damage of the throwable, an integer or a float.
<br/>`capacity` - The number of throwables a player can carry at once.
<br/>`extra_field` - A field for extra values. They will be formatted just like `damage` and `capacity`. However, `extra_field` must be formatted - there is no localization .json file for it.
<br/>`extra_value` - The value for the extra field. However, they do not need to be formatted. Type `1`, `1.5`, etc. Do not add metric units as `savetools.get_throwable_stat_dict()` will do the job.
<br/>`lock` - The requirement for unlocking this throwable.

* Add as many extra fields as wanted.
* Extra fields must be in the `title()` format. No words should start with lowercase.
* Extra values must be formatted.
* Use `savetools.get_throwable_stat_dict()` to fetch the dictionary of the data.