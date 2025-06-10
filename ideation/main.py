from ideation.generator import generate_ideas

if __name__ == "__main__":
    niche = input("Enter your content niche (e.g. fitness, finance): ")
    print("\nGenerating content ideas...\n")
    ideas = generate_ideas(niche)
    print("\n".join(ideas))
