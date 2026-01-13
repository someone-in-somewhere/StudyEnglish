package com.studyenglish.utils;

import java.util.Random;

/**
 * Generates prompts for conversation and translation practice.
 * Users copy these prompts to external AI tools (ChatGPT, Claude).
 */
public class PromptGenerator {

    private static final Random random = new Random();

    /**
     * Generate a conversation practice prompt.
     */
    public static String generateConversationPrompt(
            String topic,
            String level,
            String style,
            String length,
            String context
    ) {
        int variation = random.nextInt(10000);

        String levelDescription = getLevelDescription(level);
        String lengthDescription = getLengthDescription(length);
        String styleDescription = getStyleDescription(style);

        StringBuilder prompt = new StringBuilder();
        prompt.append("You are an English conversation partner helping me practice speaking English at ")
              .append(level).append(" level.\n\n");

        prompt.append("[Variation #").append(variation).append("] - Please create UNIQUE, ORIGINAL conversation different from any previous sessions.\n\n");

        prompt.append("CONVERSATION SETTINGS:\n");
        prompt.append("- Topic: ").append(topic).append("\n");
        prompt.append("- My Level: ").append(level).append(" (").append(levelDescription).append(")\n");
        prompt.append("- Style: ").append(style).append(" - ").append(styleDescription).append("\n");
        prompt.append("- Length: ").append(lengthDescription).append("\n");

        if (context != null && !context.isEmpty()) {
            prompt.append("- Suggested context: ").append(context).append(" (use this as inspiration but feel free to adapt)\n");
        }

        prompt.append("\nYOUR PERSONALITY & BEHAVIOR:\n");
        prompt.append("- Be patient and encouraging\n");
        prompt.append("- Use vocabulary appropriate for my level\n");
        prompt.append("- Gently correct my grammar mistakes\n");
        prompt.append("- Ask follow-up questions to keep the conversation going\n");
        prompt.append("- Provide Vietnamese translations for new words in brackets\n\n");

        prompt.append("CONVERSATION FORMAT:\n");
        prompt.append("1. Start with a greeting and introduce the topic naturally\n");
        prompt.append("2. Wait for my response before continuing\n");
        prompt.append("3. After each exchange, you can:\n");
        prompt.append("   - Correct any mistakes I made (politely)\n");
        prompt.append("   - Teach a new word/phrase related to the topic\n");
        prompt.append("   - Ask a follow-up question\n\n");

        prompt.append("Let's begin! Start the conversation.");

        return prompt.toString();
    }

    /**
     * Generate a translation practice prompt.
     */
    public static String generateTranslationPrompt(
            String topic,
            String level,
            String direction,
            String complexity,
            String passageLength
    ) {
        int variation = random.nextInt(10000);

        String levelDescription = getLevelDescription(level);
        String directionText = direction.equals("en_to_vi") ? "English to Vietnamese" : "Vietnamese to English";
        String sourceLanguage = direction.equals("en_to_vi") ? "English" : "Vietnamese";
        String targetLanguage = direction.equals("en_to_vi") ? "Vietnamese" : "English";
        String complexityDescription = getComplexityDescription(complexity);
        String lengthSentences = getPassageLengthSentences(passageLength);

        StringBuilder prompt = new StringBuilder();
        prompt.append("You are a language tutor helping me practice ").append(directionText).append(" translation.\n\n");

        prompt.append("[Variation #").append(variation).append("] - Please create UNIQUE, ORIGINAL content different from any previous sessions.\n\n");

        prompt.append("TASK: Create a translation practice exercise following these requirements:\n\n");

        prompt.append("1. PASSAGE GENERATION:\n");
        prompt.append("   - Topic: ").append(topic).append("\n");
        prompt.append("   - Level: ").append(level).append(" (").append(levelDescription).append(")\n");
        prompt.append("   - Number of sentences: ").append(lengthSentences).append("\n");
        prompt.append("   - Sentence complexity: ").append(complexityDescription).append("\n");
        prompt.append("   - Language: Write the passage in ").append(sourceLanguage).append("\n\n");

        prompt.append("2. FORMAT YOUR RESPONSE:\n");
        prompt.append("   a) First, present the ").append(sourceLanguage).append(" passage clearly\n");
        prompt.append("   b) Ask me to translate it to ").append(targetLanguage).append("\n");
        prompt.append("   c) Wait for my translation\n\n");

        prompt.append("3. AFTER I SUBMIT MY TRANSLATION:\n");
        prompt.append("   a) Show the correct/suggested translation\n");
        prompt.append("   b) Point out any errors or areas for improvement\n");
        prompt.append("   c) Explain grammar points if needed\n");
        prompt.append("   d) List new vocabulary with translations\n");
        prompt.append("   e) Give me a score from 0-10\n\n");

        prompt.append("4. VOCABULARY FORMAT:\n");
        prompt.append("   For each new word, provide:\n");
        prompt.append("   - Word (Part of speech): Vietnamese meaning\n");
        prompt.append("   - Example sentence\n\n");

        prompt.append("Please begin by generating the passage for translation.");

        return prompt.toString();
    }

    private static String getLevelDescription(String level) {
        switch (level) {
            case "A1": return "very simple vocabulary and basic grammar, short sentences, common everyday words";
            case "A2": return "elementary vocabulary and simple grammar structures";
            case "B1": return "intermediate vocabulary, compound sentences, common idioms";
            case "B2": return "upper-intermediate vocabulary, complex sentences, various tenses";
            case "C1": return "advanced vocabulary, sophisticated grammar, nuanced expressions";
            case "C2": return "near-native proficiency, complex structures, idiomatic expressions";
            default: return "appropriate vocabulary for the level";
        }
    }

    private static String getLengthDescription(String length) {
        switch (length) {
            case "short": return "5-8 exchanges (short conversation)";
            case "medium": return "10-15 exchanges (medium conversation)";
            case "long": return "20+ exchanges (extended conversation)";
            default: return "5-8 exchanges";
        }
    }

    private static String getStyleDescription(String style) {
        switch (style) {
            case "casual": return "a friendly, casual conversation between friends or acquaintances";
            case "formal": return "a polite, formal conversation in professional or official settings";
            case "business": return "a business-oriented conversation about work, meetings, or professional topics";
            default: return "a friendly conversation";
        }
    }

    private static String getComplexityDescription(String complexity) {
        switch (complexity) {
            case "simple": return "simple sentences with 5-10 words each";
            case "medium": return "medium complexity with compound sentences";
            case "complex": return "complex sentences with multiple clauses";
            default: return "simple sentences";
        }
    }

    private static String getPassageLengthSentences(String length) {
        switch (length) {
            case "short": return "5-8 sentences";
            case "medium": return "10-15 sentences";
            case "long": return "20+ sentences";
            default: return "5-8 sentences";
        }
    }

    /**
     * Get suggested contexts for conversation practice based on topic.
     */
    public static String[] getSuggestedContexts(String topic) {
        switch (topic) {
            case "Personal":
                return new String[]{
                    "talking about your family",
                    "introducing yourself to a new friend",
                    "discussing hobbies and interests",
                    "sharing weekend plans",
                    "talking about your hometown"
                };
            case "Work":
                return new String[]{
                    "discussing a project with a colleague",
                    "talking about your job responsibilities",
                    "having a job interview",
                    "discussing work-life balance",
                    "planning a team meeting"
                };
            case "Travel":
                return new String[]{
                    "booking a hotel room",
                    "asking for directions",
                    "ordering food at a restaurant",
                    "discussing travel experiences",
                    "planning a vacation"
                };
            case "Food":
                return new String[]{
                    "ordering at a restaurant",
                    "discussing favorite foods",
                    "sharing a recipe",
                    "talking about cooking",
                    "food shopping"
                };
            case "Health":
                return new String[]{
                    "visiting a doctor",
                    "discussing healthy habits",
                    "talking about exercise",
                    "describing symptoms",
                    "pharmacy visit"
                };
            case "Education":
                return new String[]{
                    "discussing studies",
                    "talking about school experiences",
                    "asking about courses",
                    "study tips and methods",
                    "career goals"
                };
            case "Technology":
                return new String[]{
                    "discussing smartphone features",
                    "talking about social media",
                    "tech support conversation",
                    "discussing apps",
                    "online shopping"
                };
            case "Entertainment":
                return new String[]{
                    "discussing movies",
                    "talking about music",
                    "planning to go out",
                    "discussing TV shows",
                    "talking about games"
                };
            default:
                return new String[]{
                    "general conversation",
                    "everyday situations",
                    "meeting new people"
                };
        }
    }
}
