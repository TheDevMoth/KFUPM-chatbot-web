import xxhash
import json
import re
import string
import numpy as np
import os
from sentence_transformers import SentenceTransformer

def _xhash(x):
    return xxhash.xxh64(x, seed=42).hexdigest()

def _xhash_list(x):
    hash_object = xxhash.xxh64(seed=42)
    for item in x:
        hash_object.update(str(item).encode())
    return hash_object.hexdigest()

def _preprocess_arabic_text(text):
    arabic_punctuations = '''`÷×؛<>_()*&^%][ـ،/:"؟.,'{}~¦+|!”…“–ـ'''
    english_punctuations = string.punctuation
    punctuations_list = arabic_punctuations + english_punctuations
    arabic_diacritics = re.compile("""ّ|َ|ً|ُ|ٌ|ِ|ٍ|ْ|ـ""", re.VERBOSE)

    # Normalize Arabic text
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    text = re.sub("گ", "ك", text)
    
    # Remove diacritics
    text = re.sub(arabic_diacritics, '', text)
    
    # Remove punctuations
    translator = str.maketrans('', '', punctuations_list)
    text = text.translate(translator)
    
    # Remove repeating characters
    text = re.sub(r'(.)\1+', r'\1', text)
    
    return text

def _cosine_similarity(vector1, vector2):
  """Calculates the cosine similarity between two vectors.

  Args:
    vector1: A NumPy array.
    vector2: A NumPy array.

  Returns:
    The cosine similarity between the two vectors.
  """

  dot_product = np.dot(vector1, vector2)
  norm1 = np.linalg.norm(vector1)
  norm2 = np.linalg.norm(vector2)

  if norm1 == 0 or norm2 == 0:
    return 0
  else:
    return (dot_product / (norm1 * norm2))

def _cosine_similarity_vec_array(vector, array):
    """Calculates the cosine similarity between a vector and an array of vectors.
    
    Args:
        vector: A NumPy array.
        array: A NumPy array.
    
    Returns:
        The cosine similarity between the vector and the array of vectors.
    """
    print(vector.shape)
    print(len(array))
    print(array[0].shape)
    dot_product = np.dot(array, vector)
    norm1 = np.linalg.norm(vector)
    norm2 = np.linalg.norm(array, axis=1)
    
    if norm1 == 0:
        return 0
    else:
        return (dot_product / (norm1 * norm2))

def _read_json(json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        return {}

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')

def _get_sentence_embeddings(sentences):
    '''
        sentences: a single string or a list of strings
        
        returns: a single vector or a list of vector embeddings
    '''
    embeddings = model.encode(sentences)
    return embeddings


# get the vector representation of the contexts
arabic_context_dict = np.load('./data/Arabic_embeddings_distiluse.npy', allow_pickle=True).item()
english_context_dict = np.load('./data/English_embeddings_distiluse.npy', allow_pickle=True).item()
context_dict = {'arabic': arabic_context_dict, 'english': english_context_dict}

arabic_hash_dict = {(_xhash(vector.data)): context for context, vector in arabic_context_dict.items()}
english_hash_dict = {(_xhash(vector.data)): context for context, vector in english_context_dict.items()}
hash_dict = {'arabic': arabic_hash_dict, 'english': english_hash_dict}

def retrieve_context(question, k=3, language='arabic'):
    '''
        question: string
        k: number of retrieved contexts
        hash_dict: dictionary of contexts and their vector representations
        context_embeddings: vector representations of the contexts
        
        returns: a list of k retrieved contexts, a list of k cosine similarities
    '''
    language = 'english' # ! for now
    context_embeddings = np.array(list(context_dict[language].values()))
    if language == 'arabic':
        question = _preprocess_arabic_text(question)
    question_embedding = _get_sentence_embeddings(question)
    cosine_similarities = _cosine_similarity_vec_array(question_embedding, context_embeddings)
    top_k_context_indices = np.argsort(cosine_similarities)[-k:][::-1]
    top_k_contexts = [hash_dict[language][_xhash(context_embeddings[i].data)] for i in top_k_context_indices]
    top_k_cosine_similarities = [cosine_similarities[i] for i in top_k_context_indices]

    return top_k_contexts, top_k_cosine_similarities
    