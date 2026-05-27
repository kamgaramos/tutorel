/* ml_filter_support.js
   Ajoute les fonctions attendues par templates/tendances.html
   (mettreAJourProduitsML, lancerPrevision, chargerProduitsML, verifierDisponibiliteDonnees)
*/

(function(){
  function $(id){ return document.getElementById(id); }

  async function fetchJSON(url){
    const r = await fetch(url);
    return r.json();
  }

  window.chargerProduitsML = async function chargerProduitsML(){
    const societe = $('ml-societe')?.value || '';
    const produitSel = $('ml-produit');
    if (!produitSel) return;

    // Tous les produits par défaut
    produitSel.innerHTML = `<option value="">Tous les produits</option>`;

    try {
      // endpoint conseillé: /api/produits (déjà existant) mais on veut filtrer par société
      // comme il n'existe pas d'endpoint dédié, on recharge depuis /api/produits et filtre côté client
      const res = await fetchJSON(`/api/produits/`);
      if (!res.success) return;
      const produits = res.produits || [];
      const filtrés = societe ? produits.filter(p => (p.societe||'') === societe) : produits;

      filtrés.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.nom; // car tu as choisi filtrer par nom
        opt.textContent = p.nom;
        produitSel.appendChild(opt);
      });
    } catch (e) {
      // fallback silencieux
    }
  };

  window.mettreAJourProduitsML = async function mettreAJourProduitsML(){
    await window.chargerProduitsML();
  };

  window.verifierDisponibiliteDonnees = function verifierDisponibiliteDonnees(){
    // UX: on ne bloque pas ici, on laisse l'API répondre
  };

  window.lancerPrevision = async function lancerPrevision(){
    const societe = $('ml-societe')?.value || '';
    const produit = $('ml-produit')?.value || '';
    const days = parseInt($('ml-horizon')?.value || '7', 10);

    const badge = $('badge-horizon');
    if (badge) badge.textContent = `${days} prochains jours`;

    const url = `/api/ml/forecast?days=${days}&societe=${encodeURIComponent(societe)}&produit=${encodeURIComponent(produit)}`;

    try {
      const data = await fetchJSON(url);
      if (!data.success){
        afficherNotif?.(data.message || 'Erreur prévision', 'error');
        return;
      }
      // renderForecast est défini dans static/js/ml.js
      if (window.afficherGraphPrevision && data.historique && data.prevision){
        window.afficherGraphPrevision(data.historique, data.prevision);
      } else if (window.charts && window.afficherGraphPrevision){
        window.afficherGraphPrevision(data.historique, data.prevision);
      }

      // Re-render secondaire
      if (societe || produit) {
        // pas de tables dédiées, on recharge au besoin
      }
    } catch (e) {
      console.error('Forecast error details:', e);
      afficherNotif?.('Erreur lors du calcul ou de l\'affichage', 'error');
    }
  };
})();

