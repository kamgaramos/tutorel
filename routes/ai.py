# routes/ai.py - Assistant IA Médical "ChatGPT Style"
from flask import Blueprint, jsonify, request, session
from database import get_db
import random
import time
import re

from services.llm_client import chat_completion, LLMClientError
from config import LLM_MAX_TURNS, LLM_TEMPERATURE_DEFAULT


ai_bp = Blueprint('ai', __name__)

# Mappage des symptômes vers les conseils/produits
# (gardé pour rétro-compatibilité UI, mais le endpoint '/chat' utilisera le LLM)
SYMPTOMES = {
    "tête": "Pour les maux de tête, le <b>Paracétamol</b> est le premier choix. Si c'est une migraine forte, l'<b>Ibuprofène</b> peut aider, mais attention à le prendre pendant un repas.",
    "fièvre": "La fièvre se traite généralement avec du <b>Paracétamol</b>. Pensez aussi à bien vous hydrater et à ne pas trop vous couvrir.",
    "ventre": "Pour les douleurs d'estomac, évitez l'aspirine ou l'ibuprofène. Préférez un antispasmodique ou demandez un antiacide si ce sont des brûlures.",
    "gorge": "Pour le mal de gorge, des collutoires ou des pastilles au miel/citron peuvent soulager. Si la déglutition est très douloureuse, consultez pour vérifier s'il s'agit d'une angine bactérienne.",
    "rhume": "Le repos et le lavage de nez à l'eau de mer sont vos meilleurs alliés. La Vitamine C peut aussi aider à renforcer vos défenses.",
    "toux": "S'agit-il d'une toux sèche ou grasse ? Pour une toux sèche, un calmant suffit. Pour une toux grasse, il faut aider à l'expectoration.",
    "fatigue": "Un complexe de <b>Vitamines</b> ou du Magnésium peut vous aider. Pensez aussi à vérifier votre sommeil.",
}

CONSEILS_AUTRES = [
    "D'une manière générale, je vous conseille de toujours lire la notice.",
    "C'est noté. Avez-vous besoin que je vérifie le stock d'un produit en particulier pour cela ?",
    "Je vois. Sachez que je peux aussi vous donner les prix si vous hésitez entre deux marques.",
    "N'oubliez pas que je suis une IA, rien ne remplace le diagnostic final de votre médecin traitant."
]

def chercher_produit_dans_db(nom_partiel):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT p.*, s.quantite FROM produits p LEFT JOIN stocks s ON p.id = s.produit_id WHERE p.nom LIKE ?", (f'%{nom_partiel}%',))
        produit = cursor.fetchone()
        conn.close()
        return dict(produit) if produit else None
    except:
        return None

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Conversation avec un LLM (ChatGPT / DeepSeek)."""
    try:
        data = request.get_json() or {}
        message = (data.get('message') or '').strip()

        if not message:
            return jsonify({'success': False, 'message': 'Message vide'}), 400

        # Historique conversation en session
        # On stocke uniquement user/assistant pour éviter d'exploser.
        history = session.get('ai_messages', [])
        if not isinstance(history, list):
            history = []

        # Limite taille: LLM_MAX_TURNS correspond à ~ (user+assistant) paires
        max_msgs = max(2, LLM_MAX_TURNS * 2)
        if len(history) > max_msgs:
            history = history[-max_msgs:]

        user_entry = {"role": "user", "content": message}
        # Appel LLM (inclut le system prompt côté client)
        res_text = chat_completion(message, history=history)

        # MAJ historique
        history.append(user_entry)
        history.append({"role": "assistant", "content": res_text})
        if len(history) > max_msgs:
            history = history[-max_msgs:]
        session['ai_messages'] = history

        # Petite note sécurité
        # (Le prompt système fait déjà le nécessaire)
        return jsonify({
            'success': True,
            'response': res_text,
            'timestamp': time.time()
        })

    except LLMClientError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'details': {
                'type': e.__class__.__name__,
            }
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'details': {
                'type': e.__class__.__name__,
            }
        }), 500



@ai_bp.route('/suggest', methods=['GET'])
def suggest():
    """Retourne des suggestions intelligentes"""
    suggestions = [
        "Quel est le prix du Doliprane ?",
        "Combien reste-t-il d'Antalgan ?",
        "Donne-moi un conseil médical",
        "Dosage de l'Ibuprofène"
    ]
    return jsonify({'success': True, 'suggestions': random.sample(suggestions, 3)})

