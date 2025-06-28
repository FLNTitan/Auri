from PIL import Image, ImageDraw, ImageFont
import requests

def create_thumbnail(base_image_path, title, subtitle="", config=None, output_path="thumbnail.jpg"):
    if config is None:
        raise ValueError("Config must be provided.")

    # Load image
    image = Image.open(base_image_path).convert("RGBA")

    # Prepare text overlay
    overlay = Image.new("RGBA", image.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype(config["font_path"], config["font_size"])

    # Calculate text size
    text = title
    if subtitle:
        text += "\n" + subtitle
    text_width, text_height = draw.multiline_textsize(text, font=font)

    # Determine position
    if config["text_position"] == "bottom":
        x = (image.width - text_width) / 2
        y = image.height - text_height - config["padding"]
    elif config["text_position"] == "top":
        x = (image.width - text_width) / 2
        y = config["padding"]
    else:
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

    # Draw background rectangle for readability
    draw.rectangle(
        [ (x - 10, y - 10), (x + text_width + 10, y + text_height + 10) ],
        fill=config["background_color"]
    )

    # Draw text
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=config["font_color"],
        align="center"
    )

    # Combine overlay and image
    combined = Image.alpha_composite(image, overlay)

    # Save final thumbnail
    combined.convert("RGB").save(output_path)
    return output_path

def generate_thumbnail_prompt(
    script_text: str,
    hashtags: str,
    platform: str,
    style: str,
    custom_style: str
) -> str:
    """
    Create a robust, platform-aware prompt for AI image generation.
    """

    # Extract main topic
    if script_text:
        main_topic = script_text.strip().split("\n")[0]
    else:
        main_topic = "social media content"

    # Clean hashtags to get keywords
    cleaned_tags = (
        ", ".join([tag.strip("#") for tag in hashtags.strip().split() if tag.startswith("#")])
        if hashtags
        else ""
    )

    # Platform-specific instructions
    platform_composition = {
        "YouTube": "bold text space, high contrast, centered composition with room for title text.",
        "TikTok": "vibrant colors, vertical framing, dynamic elements.",
        "Instagram": "clean aesthetic, minimalist composition, soft colors.",
        "LinkedIn": "professional and elegant design, clear informational space."
    }
    composition = platform_composition.get(platform, "clean and modern composition.")

    # Style keywords
    style_keywords = {
        "Clean & Modern": "clean, modern, flat design.",
        "Bold & Dynamic": "bold, dynamic, high-energy style.",
        "Playful & Fun": "playful, colorful, fun look.",
        "Minimalist & Elegant": "minimalist, elegant, sophisticated style."
    }
    style_desc = style_keywords.get(style, "clean and modern style.")

    # Custom style fallback
    custom = custom_style.strip() if custom_style else ""

    # Compose the final prompt
    prompt = (
        f"An eye-catching, high-quality digital illustration for a {platform} thumbnail about \"{main_topic}\".\n\n"
        f"Style: {style_desc} {custom}\n"
        f"Composition: {composition}\n"
        f"Keywords: {cleaned_tags if cleaned_tags else 'social media, content, viral'}.\n"
        f"Resolution: 1024x1024, crisp details, no watermark."
    )

    return prompt

def download_image(url: str, save_path: str) -> None:
    """
    Download an image from a URL to a local file.
    """
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(response.content)
