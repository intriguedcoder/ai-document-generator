import google.generativeai as genai
from app.core.config import settings
import json
import re
from app.utils.logger import get_logger
from typing import List, Dict


logger = get_logger(__name__)
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
    
    def _clean_markdown(self, content: str) -> str:
        """Remove markdown formatting artifacts from generated content"""
        # Remove bold markers
        content = content.replace('**', '')
        
        # Remove italic markers (single asterisk or underscore)
        content = re.sub(r'(?<!\*)\*(?!\*)', '', content)  # Single asterisks
        content = content.replace('_', '')
        
        # Clean up bullet points - normalize to just dash
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Remove various bullet formats: •, *, -, →, etc.
            if line:
                # If line starts with bullet-like character, normalize to dash
                if line[0] in ['•', '●', '◦', '▪', '▫', '→', '»', '*']:
                    line = '- ' + line[1:].strip()
                # Remove multiple dots/periods at start
                line = re.sub(r'^\.{2,}\s*', '', line)
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove extra spaces
        content = re.sub(r' +', ' ', content)
        
        # Remove multiple consecutive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    async def suggest_outline(self, topic: str, doc_type: str, num_sections: int) -> Dict:
        """
        AI-Generated Template (BONUS FEATURE)
        Generate outline/structure suggestions based on topic
        """
        try:
            if doc_type == "docx":
                prompt = f"""You are a professional document consultant. Generate a detailed outline for a Word document about: "{topic}"

Create exactly {num_sections} sections with:
- Section title (clear and professional)
- Brief description (2-3 sentences explaining what the section should cover)
- 3 key points to include in that section

Return ONLY valid JSON in this exact format:
{{
  "title": "Suggested Document Title",
  "sections": [
    {{
      "title": "Section Title",
      "description": "What this section covers",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}"""
            else:  # pptx
                prompt = f"""You are a presentation design expert. Generate a PowerPoint presentation outline for: "{topic}"

Create exactly {num_sections} slides with:
- Slide title (engaging and clear)
- 2-3 full-sentence ideas describing what content should go on this slide (NOT 'Point 1, Point 2, Point 3')

Return ONLY valid JSON in this exact format:
{{
  "title": "Presentation Title",
  "sections": [
    {{
      "title": "Slide Title",
      "description": "2-3 sentences describing the key ideas and content for this slide"
    }}
  ]
}}"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse JSON from response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith('```json'):
                text = text[7:-3].strip()
            elif text.startswith('```'):
                text = text[3:-3].strip()
            
            structure = json.loads(text)

            # If model still returned 'slides', normalize to 'sections'
            if doc_type == "pptx" and "slides" in structure and "sections" not in structure:
                structure["sections"] = structure.pop("slides")
            
            logger.info(f"Generated {doc_type} outline for topic: {topic}")
            return structure
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return self._get_fallback_outline(topic, doc_type, num_sections)
        except Exception as e:
            logger.error(f"Outline generation error: {str(e)}")
            return self._get_fallback_outline(topic, doc_type, num_sections)
    
    def _get_fallback_outline(self, topic: str, doc_type: str, num_sections: int) -> dict:
        """Fallback outline if AI generation fails"""
        if doc_type == "docx":
            return {
                "title": topic,
                "sections": [
                    {
                        "title": f"Section {i+1}",
                        "description": f"Content for section {i+1} about {topic}",
                        "key_points": ["Key idea 1", "Key idea 2", "Key idea 3"]
                    }
                    for i in range(num_sections)
                ]
            }
        else:  # pptx
            return {
                "title": topic,
                "sections": [
                    {
                        "title": f"Slide {i+1}",
                        "description": f"Key ideas for slide {i+1} in a presentation about {topic}.",
                    }
                    for i in range(num_sections)
                ]
            }
    
    async def generate_section_content(
        self, 
        section_title: str, 
        project_topic: str,
        context: str = "",
        tone: str = "professional",
        doc_type: str = "docx"
    ) -> str:
        """
        Generate content for a specific section/slide
        Context-aware generation based on project topic, section, and document type
        """
        try:
            tone_guidelines = {
                "professional": "Use formal, business-appropriate language. Be clear and concise.",
                "casual": "Use conversational, friendly language. Be approachable.",
                "academic": "Use scholarly language with references to research. Be precise and analytical."
            }
            
            # Different prompts for different document types
            if doc_type == "pptx":
                prompt = f"""You are creating content for a PowerPoint slide about: "{project_topic}"

Slide Title: {section_title}
Tone: {tone}
Tone Guidelines: {tone_guidelines.get(tone, tone_guidelines['professional'])}

{f"Additional Context: {context}" if context else ""}

Generate concise, impactful content for a presentation slide:
- Create 4-6 bullet points
- Each point: 15-25 words maximum  
- Be clear, actionable, and memorable
- Perfect for visual presentation
- Focus on key insights

IMPORTANT: Start directly with the bullet points. Do NOT include any introductory text like "Here is the content for your slides" or similar phrases.

Format as bullet points (one per line, start each with -)"""
            else:  # docx
                prompt = f"""You are writing content for a document about: "{project_topic}"

Section Title: {section_title}
Tone: {tone}
Tone Guidelines: {tone_guidelines.get(tone, tone_guidelines['professional'])}

{f"Additional Context: {context}" if context else ""}

Generate well-structured content for this section:
- Length: 250-350 words
- Include relevant details and examples
- Use proper paragraphs (separate with double newlines)
- Make it engaging and informative
- Ensure it flows naturally

IMPORTANT: Start directly with the content. Do NOT include any introductory text or the section title.

Write ONLY the content, no headers or titles:"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            content = response.text.strip()
            
            # Remove common unwanted introductory phrases
            unwanted_phrases = [
                "here is the content for your slides:",
                "here is the content for your slide:",
                "here are the points for your slide:",
                "here are the bullet points:",
                "here is the generated content:",
                "here's the content:",
                "content for your slide:",
                "here is the content:",
                "here are the points:",
                "slide content:",
            ]
            
            # Check and remove unwanted phrases (case-insensitive)
            content_lower = content.lower()
            for phrase in unwanted_phrases:
                if content_lower.startswith(phrase):
                    # Remove the phrase
                    content = content[len(phrase):].strip()
                    # Remove leading colon, dash, or newline if present
                    while content and content[0] in [':', '-', '\n', ' ']:
                        content = content[1:].strip()
                    break
            
            # Clean markdown formatting
            content = self._clean_markdown(content)
            
            logger.info(f"Generated {doc_type} content for section: {section_title}")
            return content
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            raise
    
    async def refine_content(self, original_content: str, refinement_prompt: str, section_title: str) -> str:
        """
        Refine existing content based on user feedback
        Maintains context and structure while applying changes
        """
        try:
            prompt = f"""You are editing content for a section titled: "{section_title}"

ORIGINAL CONTENT:
{original_content}

USER REQUEST: {refinement_prompt}

Apply the requested changes while:
- Maintaining the overall structure and flow
- Keeping relevant information
- Ensuring clarity and coherence
- Preserving the same approximate length unless specifically asked to change it

IMPORTANT: Return ONLY the refined content. Do NOT include any introductory phrases or explanations.

Return the refined content:"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            refined_content = response.text.strip()
            
            # Remove unwanted phrases from refined content too
            unwanted_phrases = [
                "here is the refined content:",
                "here's the refined version:",
                "refined content:",
                "updated content:",
            ]
            
            refined_lower = refined_content.lower()
            for phrase in unwanted_phrases:
                if refined_lower.startswith(phrase):
                    refined_content = refined_content[len(phrase):].strip()
                    while refined_content and refined_content[0] in [':', '-', '\n', ' ']:
                        refined_content = refined_content[1:].strip()
                    break
            
            # Clean markdown formatting
            refined_content = self._clean_markdown(refined_content)
            
            logger.info(f"Refined content for section: {section_title}")
            return refined_content
            
        except Exception as e:
            logger.error(f"Refinement error: {str(e)}")
            raise
