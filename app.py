#!/usr/bin/env python3
"""
Simple Flask Image Service for Easy Deployment
This can be deployed to Render, Heroku, or any simple Python hosting
"""

from flask import Flask, request, jsonify
import requests
import base64
import hashlib
from typing import Optional, List, Dict, Any

app = Flask(__name__)

# Simple in-memory cache
image_cache = {}

# Predefined educational images database
EDUCATIONAL_IMAGES = {
    "romeo_juliet_dicksee": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/DickseeRomeoandJuliet.jpg/400px-DickseeRomeoandJuliet.jpg",
        "title": "Romeo and Juliet by Frank Dicksee",
        "caption": "Romeo and Juliet by Frank Dicksee (1884) - Public Domain",
        "alt_text": "Famous painting of Romeo and Juliet embracing"
    },
    "romeo_juliet_waterhouse": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/John_William_Waterhouse_-_Juliet_-_1898.jpg/400px-John_William_Waterhouse_-_Juliet_-_1898.jpg",
        "title": "Juliet by John William Waterhouse",
        "caption": "Juliet by John William Waterhouse (1898) - Public Domain",
        "alt_text": "Painting of Juliet on her balcony"
    },
    "shakespeare_portrait": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Shakespeare.jpg/220px-Shakespeare.jpg",
        "title": "William Shakespeare Portrait",
        "caption": "William Shakespeare - The Bard",
        "alt_text": "Portrait of William Shakespeare"
    },
    "solar_system": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Planets2013.svg/450px-Planets2013.svg.png",
        "title": "Solar System Diagram",
        "caption": "The Solar System - Educational Diagram",
        "alt_text": "Diagram showing all planets in the solar system"
    },
    "dna_structure": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/DNA_Structure%2BKey%2BLabelled.pn_NoBB.png/220px-DNA_Structure%2BKey%2BLabelled.pn_NoBB.png",
        "title": "DNA Double Helix",
        "caption": "DNA Double Helix Structure",
        "alt_text": "3D model of DNA double helix"
    }
}

def download_image(url: str) -> Optional[str]:
    """Download image and return as base64"""
    try:
        # Check cache first
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in image_cache:
            return image_cache[cache_key]
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Convert to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            # Cache it
            if len(image_cache) < 20:  # Limit cache size
                image_cache[cache_key] = image_base64
            return image_base64
    except Exception as e:
        print(f"Error downloading image from {url}: {str(e)}")
    return None

def find_relevant_images(query: str, subject: str = None) -> List[Dict[str, Any]]:
    """Find relevant images based on query"""
    query_lower = query.lower()
    results = []
    
    # Check for specific matches
    if 'dicksee' in query_lower or ('romeo' in query_lower and 'juliet' in query_lower):
        results.append(EDUCATIONAL_IMAGES["romeo_juliet_dicksee"])
    elif 'juliet' in query_lower:
        results.append(EDUCATIONAL_IMAGES["romeo_juliet_waterhouse"])
    elif 'shakespeare' in query_lower:
        results.append(EDUCATIONAL_IMAGES["shakespeare_portrait"])
    elif 'solar' in query_lower or 'planet' in query_lower:
        results.append(EDUCATIONAL_IMAGES["solar_system"])
    elif 'dna' in query_lower or 'genetic' in query_lower:
        results.append(EDUCATIONAL_IMAGES["dna_structure"])
    
    # If no specific match, return based on subject
    if not results and subject:
        subject_lower = subject.lower()
        if 'english' in subject_lower or 'literature' in subject_lower:
            results.append(EDUCATIONAL_IMAGES["shakespeare_portrait"])
        elif 'science' in subject_lower or 'biology' in subject_lower:
            results.append(EDUCATIONAL_IMAGES["dna_structure"])
        elif 'astronomy' in subject_lower or 'physics' in subject_lower:
            results.append(EDUCATIONAL_IMAGES["solar_system"])
    
    # Default to Shakespeare if nothing else matches
    if not results:
        results.append(EDUCATIONAL_IMAGES["shakespeare_portrait"])
    
    return results

@app.route("/")
def root():
    return jsonify({"message": "Educational Image Service", "status": "active"})

@app.route("/fetch_image", methods=["POST"])
def fetch_image():
    """Fetch educational images based on query"""
    try:
        data = request.json
        query = data.get("query", "")
        subject = data.get("subject")
        count = data.get("count", 1)
        
        # Find relevant images
        images = find_relevant_images(query, subject)
        
        if not images:
            return jsonify({
                "success": False,
                "images": [],
                "error": "No relevant images found"
            })
        
        # Download and prepare images
        processed_images = []
        for img in images[:count]:
            # Download the image
            image_data = download_image(img["url"])
            
            processed_images.append({
                "url": img["url"] if not image_data else "",
                "data": image_data or "",
                "title": img["title"],
                "educational_caption": img["caption"],
                "alt_text": img["alt_text"],
                "source": "wikimedia"
            })
        
        return jsonify({
            "success": True,
            "images": processed_images
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "images": [],
            "error": str(e)
        })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "cache_size": len(image_cache)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)