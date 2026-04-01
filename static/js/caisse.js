// caisse.js - Gestion des ventes en temps réel
document.addEventListener('DOMContentLoaded', function () {
    // ========== ÉLÉMENTS DOM ==========
    // Formulaire de vente
    const venteForm = document.getElementById('vente-form');
    const productSelect = document.getElementById('product-select');
    const quantiteInput = document.getElementById('quantite');
    const prixVenteSpan = document.getElementById('prix-vente');
    const totalSpan = document.getElementById('total');
    const margeSpan = document.getElementById('marge');
    const btnMoins = document.getElementById('btn-moins');
    const btnPlus = document.getElementById('btn-plus');
    const btnAjouter = document.getElementById('btn-ajouter-panier');
    
    // Panier
    const panierBody = document.getElementById('panier-body');
    const panierTotalSpan = document.getElementById('panier-total');
    const panierBeneficeSpan = document.getElementById('panier-benefice');
    const btnValiderPanier = document.getElementById('btn-valider-panier');
    const btnAnnulerPanier = document.getElementById('btn-annuler-panier');
    
    // Ticket du jour
    const todayTotalSpan = document.getElementById('today-total');
    const todayBeneficeSpan = document.getElementById('today-benefice');
    const todayNbVentes = document.getElementById('today-nb-ventes');
    const ticketTable = document.getElementById('ticket-table');
    
    // Graphique
    const salesChart = document.getElementById('salesChart');
    
    // Notification
    const notification = document.getElementById('caisse-notification');
    
    // ========== ÉTAT DE L'APPLICATION ==========
    let panier = [];
    let produits = [];
    let currentProduct = null;
    
    // ========== INITIALISATION ==========
    loadProducts();
    loadTodaySales();
    loadHourlyChart();
    
    // ========== GESTIONNAIRES D'ÉVÉNEMENTS ==========
    
    /**
     * Changement de produit sélectionné
     */
    productSelect.addEventListener('change', function() {
        const productId = this.value;
        if (!productId) {
            resetProductDisplay();
            return;
        }
        
        currentProduct = produits.find(p => p.id == productId);
        if (currentProduct) {
            prixVenteSpan.textContent = currentProduct.prix_vente + ' FCFA';
            updateTotal();
            checkStock();
        }
    });
    
    /**
     * Quantité - bouton moins
     */
    btnMoins.addEventListener('click', function() {
        let qty = parseInt(quantiteInput.value) || 1;
        if (qty > 1) {
            quantiteInput.value = qty - 1;
            updateTotal();
        }
    });
    
    /**
     * Quantité - bouton plus
     */
    btnPlus.addEventListener('click', function() {
        let qty = parseInt(quantiteInput.value) || 1;
        quantiteInput.value = qty + 1;
        updateTotal();
    });
    
    /**
     * Changement manuel de quantité
     */
    quantiteInput.addEventListener('input', function() {
        let qty = parseInt(this.value) || 1;
        if (qty < 1) this.value = 1;
        updateTotal();
        checkStock();
    });
    
    /**
     * Ajouter au panier
     */
    btnAjouter.addEventListener('click', function() {
        if (!currentProduct) {
            showNotification('Sélectionnez un produit', 'error');
            return;
        }
        
        const quantite = parseInt(quantiteInput.value) || 1;
        
        // Vérifier le stock
        fetch(`/api/stocks/check/${currentProduct.id}?quantite=${quantite}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.disponible) {
                    ajouterAuPanier(currentProduct, quantite);
                } else {
                    showNotification('Stock insuffisant ! Disponible: ' + data.stock, 'error');
                }
            })
            .catch(() => showNotification('Erreur vérification stock', 'error'));
    });
    
    /**
     * Valider le panier (enregistrer la vente)
     */
    btnValiderPanier.addEventListener('click', function() {
        if (panier.length === 0) {
            showNotification('Panier vide', 'error');
            return;
        }
        
        const ventes = panier.map(item => ({
            produit_id: item.id,
            quantite: item.quantite,
            prix_unitaire: item.prix_vente
        }));
        
        fetch('/api/ventes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ventes: ventes })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Vente enregistrée avec succès', 'success');
                viderPanier();
                loadTodaySales();  // Rafraîchir le ticket du jour
                loadHourlyChart(); // Rafraîchir le graphique
                checkLowStock();   // Vérifier les alertes stock
            } else {
                showNotification(data.message || 'Erreur lors de l\'enregistrement', 'error');
            }
        })
        .catch(() => showNotification('Erreur réseau', 'error'));
    });
    
    /**
     * Annuler le panier
     */
    btnAnnulerPanier.addEventListener('click', function() {
        if (panier.length > 0 && confirm('Vider le panier ?')) {
            viderPanier();
        }
    });
    
    // ========== FONCTIONS PRINCIPALES ==========
    
    /**
     * Charger la liste des produits depuis l'API
     */
    function loadProducts() {
        fetch('/api/produits?with_stock=true')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    produits = data.produits;
                    remplirSelectProduits();
                } else {
                    showNotification('Erreur chargement produits', 'error');
                }
            })
            .catch(() => showNotification('Erreur réseau produits', 'error'));
    }
    
    /**
     * Remplir le select des produits
     */
    function remplirSelectProduits() {
        productSelect.innerHTML = '<option value="">-- Choisir un produit --</option>';
        
        // Grouper par société
        const societes = ['SABC', 'UCB', 'Guinness', 'Sources', 'Autres'];
        
        societes.forEach(societe => {
            const produitsSociete = produits.filter(p => p.societe === societe);
            if (produitsSociete.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = societe;
                
                produitsSociete.forEach(p => {
                    const option = document.createElement('option');
                    option.value = p.id;
                    option.textContent = `${p.nom} - ${p.prix_vente} FCFA (Stock: ${p.stock})`;
                    if (p.stock <= 0) option.disabled = true;
                    optgroup.appendChild(option);
                });
                
                productSelect.appendChild(optgroup);
            }
        });
    }
    
    /**
     * Ajouter un produit au panier
     */
    function ajouterAuPanier(produit, quantite) {
        // Vérifier si le produit est déjà dans le panier
        const existing = panier.find(item => item.id === produit.id);
        
        if (existing) {
            existing.quantite += quantite;
        } else {
            panier.push({
                id: produit.id,
                nom: produit.nom,
                prix_achat: produit.prix_achat,
                prix_vente: produit.prix_vente,
                quantite: quantite,
                societe: produit.societe
            });
        }
        
        renderPanier();
        updatePanierTotals();
        
        // Réinitialiser la quantité
        quantiteInput.value = 1;
        
        showNotification(`${produit.nom} ajouté au panier`, 'success');
    }
    
    /**
     * Afficher le panier dans le tableau
     */
    function renderPanier() {
        panierBody.innerHTML = '';
        
        panier.forEach((item, index) => {
            const row = panierBody.insertRow();
            row.insertCell(0).textContent = item.nom;
            row.insertCell(1).textContent = item.quantite;
            row.insertCell(2).textContent = item.prix_vente + ' FCFA';
            
            const total = item.quantite * item.prix_vente;
            row.insertCell(3).textContent = total + ' FCFA';
            
            const benefice = item.quantite * (item.prix_vente - item.prix_achat);
            row.insertCell(4).textContent = benefice + ' FCFA';
            
            // Bouton supprimer
            const actions = row.insertCell(5);
            const btnSuppr = document.createElement('button');
            btnSuppr.textContent = '×';
            btnSuppr.className = 'btn-supprimer';
            btnSuppr.onclick = () => supprimerDuPanier(index);
            actions.appendChild(btnSuppr);
        });
    }
    
    /**
     * Supprimer un élément du panier
     */
    function supprimerDuPanier(index) {
        panier.splice(index, 1);
        renderPanier();
        updatePanierTotals();
    }
    
    /**
     * Vider le panier
     */
    function viderPanier() {
        panier = [];
        renderPanier();
        updatePanierTotals();
    }
    
    /**
     * Mettre à jour les totaux du panier
     */
    function updatePanierTotals() {
        const total = panier.reduce((sum, item) => sum + (item.quantite * item.prix_vente), 0);
        const benefice = panier.reduce((sum, item) => sum + (item.quantite * (item.prix_vente - item.prix_achat)), 0);
        
        panierTotalSpan.textContent = total + ' FCFA';
        panierBeneficeSpan.textContent = benefice + ' FCFA';
    }
    
    /**
     * Mettre à jour le total et la marge pour le produit sélectionné
     */
    function updateTotal() {
        if (!currentProduct) return;
        
        const quantite = parseInt(quantiteInput.value) || 1;
        const total = quantite * currentProduct.prix_vente;
        const marge = quantite * (currentProduct.prix_vente - currentProduct.prix_achat);
        
        totalSpan.textContent = total + ' FCFA';
        margeSpan.textContent = marge + ' FCFA';
    }
    
    /**
     * Vérifier le stock pour le produit sélectionné
     */
    function checkStock() {
        if (!currentProduct) return;
        
        const quantite = parseInt(quantiteInput.value) || 1;
        const stockClass = document.querySelector('.stock-indicator');
        
        if (stockClass) {
            if (currentProduct.stock < quantite) {
                stockClass.className = 'stock-indicator stock-rupture';
                stockClass.textContent = '⚠️ Stock insuffisant';
                btnAjouter.disabled = true;
            } else if (currentProduct.stock < 5) {
                stockClass.className = 'stock-indicator stock-faible';
                stockClass.textContent = `⚠️ Stock faible: ${currentProduct.stock} restants`;
                btnAjouter.disabled = false;
            } else {
                stockClass.className = 'stock-indicator stock-ok';
                stockClass.textContent = `✓ Stock: ${currentProduct.stock}`;
                btnAjouter.disabled = false;
            }
        }
    }
    
    /**
     * Réinitialiser l'affichage produit
     */
    function resetProductDisplay() {
        prixVenteSpan.textContent = '0 FCFA';
        totalSpan.textContent = '0 FCFA';
        margeSpan.textContent = '0 FCFA';
        currentProduct = null;
    }
    
    /**
     * Charger les ventes du jour
     */
    function loadTodaySales() {
        fetch('/api/ventes/aujourdhui')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mettre à jour les KPIs
                    todayTotalSpan.textContent = data.total + ' FCFA';
                    todayBeneficeSpan.textContent = data.benefice + ' FCFA';
                    todayNbVentes.textContent = data.nb_ventes;
                    
                    // Remplir le tableau des tickets
                    renderTicketTable(data.ventes);
                }
            })
            .catch(() => showNotification('Erreur chargement ventes', 'error'));
    }
    
    /**
     * Afficher le tableau des tickets
     */
    function renderTicketTable(ventes) {
        if (!ticketTable) return;
        
        const tbody = ticketTable.querySelector('tbody') || ticketTable;
        tbody.innerHTML = '';
        
        ventes.forEach(vente => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = vente.heure;
            row.insertCell(1).textContent = vente.produit;
            row.insertCell(2).textContent = vente.quantite;
            row.insertCell(3).textContent = vente.montant + ' FCFA';
        });
    }
    
    /**
     * Charger le graphique des ventes par heure
     */
    function loadHourlyChart() {
        if (!salesChart) return;
        
        fetch('/api/ventes/par-heure')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    renderHourlyChart(data.heures, data.montants);
                }
            })
            .catch(() => console.error('Erreur chargement graphique'));
    }
    
    /**
     * Afficher le graphique horaire avec Chart.js
     */
    function renderHourlyChart(heures, montants) {
        const ctx = salesChart.getContext('2d');
        
        // Détruire l'ancien graphique s'il existe
        if (window.hourlyChartInstance) {
            window.hourlyChartInstance.destroy();
        }
        
        window.hourlyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: heures,
                datasets: [{
                    label: 'Ventes (FCFA)',
                    data: montants,
                    backgroundColor: '#ff9800',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' FCFA';
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Vérifier les stocks faibles après une vente
     */
    function checkLowStock() {
        fetch('/api/stocks/faibles')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.produits.length > 0) {
                    const msg = `⚠️ Stock faible: ${data.produits.map(p => p.nom).join(', ')}`;
                    showNotification(msg, 'warning');
                }
            })
            .catch(() => {});
    }
    
    // ========== NOTIFICATIONS ==========
    
    function showNotification(message, type) {
        if (!notification) return;
        
        notification.textContent = message;
        notification.className = 'notification ' + type;
        notification.style.display = 'block';
        
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }
});