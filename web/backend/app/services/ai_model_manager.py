"""
AI Model Manager with lazy loading and memory management.
Handles all local AI models: Qwen (GGUF), T5, NLLB, and embedding models.
"""

import gc
import json
import logging
import re
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List

import torch

from app.config import settings

logger = logging.getLogger(__name__)


class AIModelManager:
    """
    Singleton manager for all AI models with lazy loading.

    Models are loaded on first use and can be unloaded to free memory.
    Supports:
    - Qwen2.5-7B for text generation (vocabulary, exercises, reading, chat)
    - T5-base for grammar correction
    - NLLB-200 for translation (EN-VI)
    - BGE-large for embeddings
    - Multilingual-mpnet for sentence similarity
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._models: Dict[str, Any] = {}
        self._tokenizers: Dict[str, Any] = {}
        self._model_locks: Dict[str, threading.Lock] = {
            "qwen": threading.Lock(),
            "t5": threading.Lock(),
            "nllb": threading.Lock(),
            "bge": threading.Lock(),
            "multilingual": threading.Lock(),
        }

        # Check device availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"AI Model Manager initialized. Device: {self.device}")

        # Track model status
        self._model_status: Dict[str, bool] = {
            "qwen": False,
            "t5": False,
            "nllb": False,
            "bge": False,
            "multilingual": False,
        }

    @property
    def models_dir(self) -> Path:
        """Get the models directory path."""
        return settings.AI_MODELS_DIR

    def get_model_status(self) -> Dict[str, bool]:
        """Get the loading status of all models."""
        return self._model_status.copy()

    def check_model_files(self) -> Dict[str, bool]:
        """Check if model files exist."""
        qwen_path = self.models_dir / settings.QWEN_MODEL_PATH
        return {
            "qwen": qwen_path.exists(),
            "t5": True,  # Downloaded on demand from HuggingFace
            "nllb": True,
            "bge": True,
            "multilingual": True,
        }

    # ==================== Qwen Model ====================

    def _load_qwen(self) -> bool:
        """Load Qwen model using llama-cpp-python."""
        if self._model_status["qwen"]:
            return True

        with self._model_locks["qwen"]:
            if self._model_status["qwen"]:
                return True

            try:
                from llama_cpp import Llama

                model_path = self.models_dir / settings.QWEN_MODEL_PATH

                if not model_path.exists():
                    logger.warning(f"Qwen model not found at {model_path}. Using fallback mode.")
                    self._models["qwen"] = None
                    self._model_status["qwen"] = True
                    return True

                logger.info(f"Loading Qwen model from {model_path}")

                self._models["qwen"] = Llama(
                    model_path=str(model_path),
                    n_ctx=settings.QWEN_N_CTX,
                    n_threads=settings.QWEN_N_THREADS,
                    n_gpu_layers=settings.QWEN_N_GPU_LAYERS,
                    verbose=settings.DEBUG,
                )

                self._model_status["qwen"] = True
                logger.info("Qwen model loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load Qwen model: {e}")
                self._models["qwen"] = None
                self._model_status["qwen"] = True  # Mark as "loaded" in fallback mode
                return False

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        stop: List[str] = None
    ) -> str:
        """
        Generate text using Qwen model.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences

        Returns:
            Generated text
        """
        self._load_qwen()

        max_tokens = max_tokens or settings.MAX_TOKENS
        temperature = temperature or settings.TEMPERATURE
        stop = stop or ["</s>", "\n\n\n"]

        if self._models.get("qwen") is None:
            # Fallback mode - return mock data for development
            return self._generate_fallback(prompt)

        try:
            result = self._models["qwen"](
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop,
                echo=False,
            )

            return result["choices"][0]["text"].strip()

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return self._generate_fallback(prompt)

    def _generate_fallback(self, prompt: str) -> str:
        """Generate fallback response when model is unavailable."""
        # Check what type of content is being requested
        prompt_lower = prompt.lower()

        if "vocabulary" in prompt_lower or "words" in prompt_lower:
            return json.dumps([
                {
                    "word": "example",
                    "meaning_vi": "ví dụ",
                    "pronunciation": "/ɪɡˈzæmpəl/",
                    "part_of_speech": "noun",
                    "example_en": "This is an example sentence.",
                    "example_vi": "Đây là một câu ví dụ.",
                    "synonyms": ["instance", "sample"]
                }
            ])

        if "reading" in prompt_lower or "passage" in prompt_lower:
            return json.dumps({
                "title": "Sample Reading Passage",
                "passage": "This is a sample reading passage for testing purposes. It contains several sentences to demonstrate the reading comprehension feature.",
                "questions": [
                    {
                        "question": "What is this passage about?",
                        "options": ["Testing", "Reading", "Writing", "Speaking"],
                        "answer": 0
                    }
                ]
            })

        if "exercise" in prompt_lower:
            return json.dumps([
                {
                    "question": "Fill in the blank: This is a ___ sentence.",
                    "answer": "test",
                    "options": ["test", "real", "fake", "new"]
                }
            ])

        # Default chat response
        return "I understand your message. This is a development response as the AI model is not loaded."

    # ==================== T5 Grammar Model ====================

    def _load_t5(self) -> bool:
        """Load T5 grammar correction model."""
        if self._model_status["t5"]:
            return True

        with self._model_locks["t5"]:
            if self._model_status["t5"]:
                return True

            try:
                from transformers import T5ForConditionalGeneration, T5Tokenizer

                logger.info(f"Loading T5 grammar model: {settings.T5_GRAMMAR_MODEL}")

                self._tokenizers["t5"] = T5Tokenizer.from_pretrained(
                    settings.T5_GRAMMAR_MODEL,
                    cache_dir=str(self.models_dir / "cache")
                )
                self._models["t5"] = T5ForConditionalGeneration.from_pretrained(
                    settings.T5_GRAMMAR_MODEL,
                    cache_dir=str(self.models_dir / "cache")
                )

                if self.device == "cuda":
                    self._models["t5"] = self._models["t5"].to(self.device)

                self._model_status["t5"] = True
                logger.info("T5 grammar model loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load T5 model: {e}")
                self._models["t5"] = None
                self._tokenizers["t5"] = None
                self._model_status["t5"] = True
                return False

    def correct_grammar(self, text: str) -> Dict[str, Any]:
        """
        Correct grammar in text using T5 model.

        Args:
            text: Text to correct

        Returns:
            Dictionary with corrected text and list of corrections
        """
        self._load_t5()

        if self._models.get("t5") is None:
            return {"corrected": text, "corrections": [], "has_errors": False}

        try:
            # Prepare input
            input_text = f"grammar: {text}"
            inputs = self._tokenizers["t5"](
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate correction
            outputs = self._models["t5"].generate(
                **inputs,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )

            corrected = self._tokenizers["t5"].decode(
                outputs[0],
                skip_special_tokens=True
            )

            # Find corrections
            corrections = self._find_corrections(text, corrected)

            return {
                "corrected": corrected,
                "corrections": corrections,
                "has_errors": len(corrections) > 0
            }

        except Exception as e:
            logger.error(f"Grammar correction failed: {e}")
            return {"corrected": text, "corrections": [], "has_errors": False}

    def _find_corrections(self, original: str, corrected: str) -> List[Dict[str, str]]:
        """Find differences between original and corrected text."""
        corrections = []

        if original.strip() == corrected.strip():
            return corrections

        # Simple word-level comparison
        orig_words = original.split()
        corr_words = corrected.split()

        # Use sequence matching for better diff
        from difflib import SequenceMatcher
        matcher = SequenceMatcher(None, orig_words, corr_words)

        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "replace":
                corrections.append({
                    "original": " ".join(orig_words[i1:i2]),
                    "corrected": " ".join(corr_words[j1:j2]),
                    "explanation": "Word/phrase replaced",
                    "error_type": "grammar"
                })
            elif op == "insert":
                corrections.append({
                    "original": "",
                    "corrected": " ".join(corr_words[j1:j2]),
                    "explanation": "Missing word/phrase added",
                    "error_type": "grammar"
                })
            elif op == "delete":
                corrections.append({
                    "original": " ".join(orig_words[i1:i2]),
                    "corrected": "",
                    "explanation": "Unnecessary word/phrase removed",
                    "error_type": "grammar"
                })

        return corrections

    # ==================== NLLB Translation Model ====================

    def _load_nllb(self) -> bool:
        """Load NLLB translation model."""
        if self._model_status["nllb"]:
            return True

        with self._model_locks["nllb"]:
            if self._model_status["nllb"]:
                return True

            try:
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

                logger.info(f"Loading NLLB model: {settings.NLLB_MODEL}")

                self._tokenizers["nllb"] = AutoTokenizer.from_pretrained(
                    settings.NLLB_MODEL,
                    cache_dir=str(self.models_dir / "cache")
                )
                self._models["nllb"] = AutoModelForSeq2SeqLM.from_pretrained(
                    settings.NLLB_MODEL,
                    cache_dir=str(self.models_dir / "cache")
                )

                if self.device == "cuda":
                    self._models["nllb"] = self._models["nllb"].to(self.device)

                self._model_status["nllb"] = True
                logger.info("NLLB model loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load NLLB model: {e}")
                self._models["nllb"] = None
                self._tokenizers["nllb"] = None
                self._model_status["nllb"] = True
                return False

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between English and Vietnamese.

        Args:
            text: Text to translate
            source_lang: Source language code (en/vi)
            target_lang: Target language code (en/vi)

        Returns:
            Translated text
        """
        self._load_nllb()

        if self._models.get("nllb") is None:
            # Fallback
            if target_lang == "vi":
                return f"[Bản dịch của: {text}]"
            return f"[Translation of: {text}]"

        try:
            # NLLB language codes
            lang_codes = {
                "en": "eng_Latn",
                "vi": "vie_Latn"
            }

            src_lang = lang_codes.get(source_lang, "eng_Latn")
            tgt_lang = lang_codes.get(target_lang, "vie_Latn")

            # Set source language
            self._tokenizers["nllb"].src_lang = src_lang

            # Tokenize
            inputs = self._tokenizers["nllb"](
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )

            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate translation
            forced_bos_token_id = self._tokenizers["nllb"].lang_code_to_id[tgt_lang]

            outputs = self._models["nllb"].generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )

            translated = self._tokenizers["nllb"].decode(
                outputs[0],
                skip_special_tokens=True
            )

            return translated

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            if target_lang == "vi":
                return f"[Bản dịch của: {text}]"
            return f"[Translation of: {text}]"

    # ==================== Embedding Models ====================

    def _load_bge(self) -> bool:
        """Load BGE embedding model."""
        if self._model_status["bge"]:
            return True

        with self._model_locks["bge"]:
            if self._model_status["bge"]:
                return True

            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading BGE model: {settings.BGE_MODEL}")

                self._models["bge"] = SentenceTransformer(
                    settings.BGE_MODEL,
                    cache_folder=str(self.models_dir / "cache")
                )

                if self.device == "cuda":
                    self._models["bge"] = self._models["bge"].to(self.device)

                self._model_status["bge"] = True
                logger.info("BGE model loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load BGE model: {e}")
                self._models["bge"] = None
                self._model_status["bge"] = True
                return False

    def _load_multilingual(self) -> bool:
        """Load multilingual embedding model."""
        if self._model_status["multilingual"]:
            return True

        with self._model_locks["multilingual"]:
            if self._model_status["multilingual"]:
                return True

            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading multilingual model: {settings.MULTILINGUAL_MODEL}")

                self._models["multilingual"] = SentenceTransformer(
                    settings.MULTILINGUAL_MODEL,
                    cache_folder=str(self.models_dir / "cache")
                )

                if self.device == "cuda":
                    self._models["multilingual"] = self._models["multilingual"].to(self.device)

                self._model_status["multilingual"] = True
                logger.info("Multilingual model loaded successfully")
                return True

            except Exception as e:
                logger.error(f"Failed to load multilingual model: {e}")
                self._models["multilingual"] = None
                self._model_status["multilingual"] = True
                return False

    def get_embeddings(
        self,
        texts: List[str],
        model: str = "bge"
    ) -> Optional[List[List[float]]]:
        """
        Get embeddings for texts.

        Args:
            texts: List of texts to embed
            model: Model to use ("bge" or "multilingual")

        Returns:
            List of embedding vectors
        """
        if model == "bge":
            self._load_bge()
            model_obj = self._models.get("bge")
        else:
            self._load_multilingual()
            model_obj = self._models.get("multilingual")

        if model_obj is None:
            return None

        try:
            embeddings = model_obj.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        model: str = "multilingual"
    ) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            model: Model to use

        Returns:
            Similarity score (0-1)
        """
        embeddings = self.get_embeddings([text1, text2], model)

        if embeddings is None:
            return 0.5  # Default similarity

        import numpy as np

        vec1 = np.array(embeddings[0])
        vec2 = np.array(embeddings[1])

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)

    # ==================== Memory Management ====================

    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model to free memory.

        Args:
            model_name: Name of model to unload

        Returns:
            True if successful
        """
        if model_name not in self._model_locks:
            return False

        with self._model_locks[model_name]:
            if model_name in self._models:
                del self._models[model_name]
            if model_name in self._tokenizers:
                del self._tokenizers[model_name]

            self._model_status[model_name] = False

            # Force garbage collection
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info(f"Unloaded model: {model_name}")
            return True

    def unload_all(self) -> None:
        """Unload all models to free memory."""
        for model_name in list(self._models.keys()):
            self.unload_model(model_name)

        logger.info("All models unloaded")

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        result = {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024),
            "loaded_models": [k for k, v in self._model_status.items() if v],
        }

        if torch.cuda.is_available():
            result["gpu_allocated_mb"] = torch.cuda.memory_allocated() / (1024 * 1024)
            result["gpu_cached_mb"] = torch.cuda.memory_reserved() / (1024 * 1024)

        return result


# Global instance
ai_manager = AIModelManager()
