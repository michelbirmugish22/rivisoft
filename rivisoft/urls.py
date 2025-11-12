from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from riviapp.view import views, auth_views, nav_views, views_operations, reservation_pdf,checkin_pdf, predictor, visualisation
from riviapp.rapports import facture_vente, recu_paiement, journal_caisse, rapports_du_stock, bulletin_paie, liste_employes, breakfastlist

urlpatterns = [
    path('authentification/auth/',auth_views.connexion, name="login"),
    path('d-e-c',auth_views.deconnexion, name="logout"),
    path('i-e-c',auth_views.inscription, name="signin"),
    path('change_password',auth_views.change_password, name="change_password"),
    path('i-e-edit',auth_views.edit_user, name="edit_user"),
    path('ibloquer_user/<str:username>/',auth_views.bloquer_user, name="bloc_user"),
    path('', views.home, name="home"),
    path('rivisoft/', views.home, name="home2"),
    path('rivisoft/home', views.index, name="index2"),
    path('rivisoft/analyseia', views.analyseia, name="analyseia"),
    path('rivisoft/informations', views.informations, name="informations"),
    path('rivisoft/load_notifications', views.load_notifications, name="load_notifications"),
    path('rivisoft/load_commande_fact', views.load_commande_fact, name="load_commande_fact"),
    path('rivisoft/info_client_chambre/<int:id_cli>/', views.info_client_chambre, name="info_client_chambre"),
    # --------------------------- URLS DE NAVIGATION ASSYNCRONE -------------------
    path('home', views.index, name="index"),
    path('rivisoft/g-clients/', views.gest_clients, name="gest_clients"),
    path('rivisoft/g-caisse/', views.caisse, name="caisse"),
    path('rivisoft/g-post_operation_caisse/', views.post_operation_caisse, name="post_operation_caisse"),
    path('rivisoft/g-night_audit/', views.night_audit, name="night_audit"),
    path('rivisoft/g-make_night_audit/', views.make_night_audit, name="make_night_audit"),
    path('rivisoft/g-demande_achat/', views.demande_achat, name="demande_achat"),
    path('rivisoft/g-demande_stock/', views.demande_stock, name="demande_stock"),
    path('rivisoft/g-entree_stock/', views.entree_stock, name="entree_stock"),
    path('rivisoft/g-sortie_stock/', views.sortie_stock, name="sortie_stock"),
    path('rivisoft/g-rapports_stock/', views.rapports_stock, name="rapports_stock"),
    path('rivisoft/g-menu/', nav_views.menumaster, name="menumaster"),
    path('rivisoft/g-employes/', nav_views.employes, name="employes"),
    path('rivisoft/g-registre_employes/', nav_views.registre_employes, name="registre_employes"),
    path('rivisoft/g-bases_salariales/', nav_views.bases_salariales, name="bases_salariales"),
    path('rivisoft/g-octroi_prets/', nav_views.octroi_prets, name="octroi_prets"),
    path('rivisoft/g-bloc/', nav_views.bloc, name="bloc"),
    path('rivisoft/g-chambre/', nav_views.chambre, name="chambre"), 
    path('rivisoft/g-statut_chambre/', nav_views.statut_chambre, name="statut_cha"),
    path('rivisoft/g-statut_salles/', nav_views.statut_salles, name="statut_salles"),
    path('rivisoft/g-rsv_salle_form/', nav_views.rsv_salle_form, name="rsv_salle_form"),
    path('rivisoft/g-deposit_form/', nav_views.deposit_form, name="deposit_form"),
    path('rivisoft/g-checkout_form/', nav_views.checkout_form, name="checkout_form"),
    path('rivisoft/g-salle/', nav_views.salle, name="salle"),
    path('rivisoft/g-pdv/', nav_views.pdv, name="pdv"),
    path('rivisoft/g-entreprise/', nav_views.entreprise, name="entreprise"),
    path('rivisoft/g-fournisseur/', nav_views.fournisseur, name="fournisseur"),
    path('rivisoft/g-stock/', nav_views.stock, name="stock"),
    path('rivisoft/g-departement/', nav_views.departement, name="departement"),
    path('rivisoft/g-arevenu/', nav_views.arevenu, name="arevenu"),
    path('rivisoft/g-fact/', nav_views.fact, name="fact"),
    path('rivisoft/g-reservation/', nav_views.reservation, name="reservation"),
    path('rivisoft/g-checkin_page/', nav_views.checkin_page, name="checkin_page"),
    path('rivisoft/g-article/', nav_views.article, name="article"),
    
    
    
    
    
    
    
    
    
    #URLS GESTION CLIENTS --------------------------------------------------
    path('requetes-client-put/', views.PutClient.as_view(), name='put_client'),
    path('requetes-client-postget/', views.PostGetClient.as_view(), name='post_get_client'),
    path('delete_client/', views.delete_client, name="delete_client"),
        #URLS GESTION EMPLOYERS --------------------------------------------------
    path('requetes-save_categorie_employe/', views.save_categorie_employe, name='save_categorie_employe'),
    path('requetes-put_categorie_employe/', views.edit_categorie_employe, name='edit_categorie_employe'),
    path('requetes-delete_categorie_employe/', views.delete_categorie_employe, name='delete_categorie_employe'),
    #URLS GESTION EMPLOYERS --------------------------------------------------
    path('requetes-save_employe/', views.save_employe, name='save_employe'),
    path('requetes-put_employe/', views.edit_employe, name='edit_employe'),
    path('requetes-delete_employe/', views.delete_employe, name='delete_employe'),
        #URLS GESTION MENU --------------------------------------------------
    path('requetes-save-gmenu/', views.save_groupemenu, name='save_groupemenu'),
    path('requetes-put-gmenu/', views.edit_groupemenu, name='edit_groupemenu'),
    path('requetes-delete-gmenu/', views.delete_groupemenu, name='delete_groupemenu'),
    #URLS GESTION MENU --------------------------------------------------
    path('requetes-save-menu/', views.save_menu, name='save_menu'),
    path('requetes-put-menu/', views.edit_menu, name='edit_menu'),
    path('requetes-delete-menu/', views.delete_menu, name='delete_menu'),
    #URLS GESTION BLOC --------------------------------------------------
    path('requetes-save-bloc/', views.save_bloc, name='save_bloc'),
    path('requetes-put-bloc/', views.edit_bloc, name='edit_bloc'),
    path('requetes-delete-bloc/', views.delete_bloc, name='delete_bloc'),
    #URLS GESTION CATEGORIES --------------------------------------------------
    path('requetes-save-cat/', views.save_cat, name='save_cat'),
    path('requetes-put-cat/', views.edit_cat, name='edit_cat'),
    path('requetes-delete-cat/', views.delete_cat, name='delete_cat'),
    #URLS GESTION CHAMBRES --------------------------------------------------
    path('requetes-save-cha/', views.save_chambre, name='save_chambre'),
    path('requetes-put-cha/', views.edit_chambre, name='edit_chambre'),
    path('requetes-delete-cha/', views.delete_chambre, name='delete_chambre'),
    path('rivisoft-rooms/avalability/', views.chambres_dispos, name='chambres_dispos'),
    #URLS GESTION BOUTIQUES --------------------------------------------------
    path('requetes-save-bout/', views.save_bout, name='save_bout'),
    path('requetes-put-bout/', views.edit_bout, name='edit_bout'),
    path('requetes-delete-bout/', views.delete_bout, name='delete_bout'),
    #URLS GESTION SALLES --------------------------------------------------
    path('requetes-save-salle/', views.save_salle, name='save_salle'),
    path('requetes-put-salle/', views.edit_salle, name='edit_salle'),
    path('requetes-delete-salle/', views.delete_salle, name='delete_salle'),
    #URLS GESTION POINTS DE VENTE --------------------------------------------------
    path('requetes-save-pdv/', views.save_pdv, name='save_pdv'),
    path('requetes-put-pdv/', views.edit_pdv, name='edit_pdv'),
    path('requetes-delete-pdv/', views.delete_pdv, name='delete_pdv'),
    #URLS CREATION ENTREPRISE--------------------------------------------------
    path('requetes-save-entreprise/', views.save_entreprise, name='save_entreprise'),
    path('requetes-put-entreprise/', views.edit_entreprise, name='edit_entreprise'),
    path('requetes-delete-entreprise/', views.delete_entreprise, name='delete_entreprise'),
    #URLS CREATION ENTREPRISE--------------------------------------------------
    path('requetes-save-fournisseur/', views.save_fournisseur, name='save_fournisseur'),
    path('requetes-put-fournisseur/', views.edit_fournisseur, name='edit_fournisseur'),
    path('requetes-delete-fournisseur/', views.delete_fournisseur, name='delete_fournisseur'),
    #URLS CREATION DEPARTEMENT--------------------------------------------------
    path('requetes-save-departement/', views.save_departement, name='save_departement'),
    path('requetes-put-departement/', views.edit_departement, name='edit_departement'),
    path('requetes-delete-departement/', views.delete_departement, name='delete_departement'),
     #URLS CREATION DEPARTEMENT--------------------------------------------------
    path('requetes-save-service/', views.save_service, name='save_service'),
    path('requetes-put-service/', views.edit_service, name='edit_service'),
    path('requetes-delete-service/', views.delete_service, name='delete_service'),
    #URLS CREATION STOCKS--------------------------------------------------
    path('requetes-save-stock/', views.save_stock, name='save_stock'),
    path('requetes-put-stock/', views.edit_stock, name='edit_stock'),
    path('requetes-delete-stock/', views.delete_stock, name='delete_stock'),
    #URLS CREATION GROUPE ARTICLES--------------------------------------------------
    path('requetes-save_groupe_article/', views.save_groupe_article, name='save_groupe_article'),
    path('requetes-edit_groupe_article/', views.edit_groupe_article, name='edit_groupe_article'),
    path('requetes-delete_groupe_article/', views.delete_groupe_article, name='delete_groupe_article'),
    #URLS CREATION ARTICLES--------------------------------------------------
    path('requetes-save_article/', views.save_article, name='save_article'),
    path('requetes-edit_article', views.edit_article, name='edit_article'),
    path('requetes-delete_article/', views.delete_article, name='delete_article'),
    #URLS CREATION AUTRES REVENUES--------------------------------------------------
    path('requetes-save-arevenu/', views.save_arevenu, name='save_arevenu'),
    path('requetes-put-arevenu/', views.edit_arevenu, name='edit_arevenu'),
    path('requetes-delete-arevenu/', views.delete_arevenu, name='delete_arevenu'),
     #URLS CREATION AUTRES REVENUES--------------------------------------------------
    path('requetes-save_atarif/', views.save_atarif, name='save_atarif'),
    path('requetes-put-atarif/', views.edit_atarif, name='edit_atarif'),
    path('requetes-delete-atarif/', views.delete_atarif, name='delete_atarif'),
    #URLS OPERATIONS QUOTIDIENNES --------------------------------------------------
    path('requetes-demande_achat_url/', views_operations.commande_achat, name='demande_achat_url'),
    path('requetes-demande_stock_url/', views_operations.commande_stock, name='demande_stock_url'),
    path('requetes-authoriser_commande_achat/', views_operations.authoriser_commande_achat, name='authoriser_commande_achat'),
    path('requetes-entree_stock_url/', views_operations.entree_stock, name='entree_stock_url'),
    path('requetes-sortie_stock_url/', views_operations.sortie_stock, name='sortie_stock_url'),
    path('requetes-vente/', views_operations.vente, name='vente_url'),
    path('requetes-annuler-facture/', views_operations.annuler_facture, name='annuler_facture'),
    path('requets-payer facture de vente/', views_operations.payer_facture_vente,name='payer_facture_vente'),
    path('requetes-annuler-reservation/', views_operations.reservation, name='enreg_reservation'),
    path('requetes-edit_reservation/', views_operations.edit_reservation, name='edit_reservation'),
    path('requetes-delete_reservation/', views_operations.delete_reservation, name='delete_reservation'),
    path('requetes-annuler-get_rsv/', views_operations.get_one_reservations, name='get_one_reservations'),
    path('requetes-annuler-checkinclient/', views_operations.checkin, name='checkinclient'),
    path('rivisoft/g-change_status_chambre/', views_operations.change_status_chambre, name="change_status_chambre"),
    path('requetes-annuler-deposit_chambre/', views_operations.deposit_chambre, name='deposit_chambre'),
    path('requetes-remuneration_employes/', views_operations.remuneration_employes, name='remuneration_employes'),
    path('requetes-octroyer_pret/', views_operations.octroyer_pret, name='octroyer_pret'),
    path('requetes-rapports_reception/', views_operations.rapports_reception, name='rapports_reception'),
    path('requetes-rapports_ress_hum/', views_operations.rapports_ress_hum, name='rapports_ress_hum'),
    path('requetes-rapports_ress_hum_print/', liste_employes.index, name='rapports_ress_hum_print'),
    path('requetes-suivie_creances/', views_operations.suivie_creances, name='suivie_creances'),
    
    
    
    
    
    
    
    
    
    # ----------------------------LES RAPPORTS PDF ------------------------------------------
    path('generate-invoice/', reservation_pdf.index, name='reservation_pdf'),
    path('generate-checkin_pdf/', checkin_pdf.index, name='checkin_pdf'),
    path('generate-breakfastlist/', breakfastlist.index, name='breakfastlist'),
    path('generate-liste_chambres/',visualisation.liste_chambres, name='liste_chambres'),
    path('generate-statut_chambres/',visualisation.statut_chambres, name='statut_chambres'),
    path('generate-liste_reservations/',visualisation.liste_rsv, name='liste_rsv'),
    path('generate-facture_vente/<int:id_fact>/',facture_vente.vente, name='facture_vente'),
    path('generate-recu_de_payement_accomodation/<int:num>/',recu_paiement.index, name='recu_de_payement'),
    path('generate-bulletin_paie/<int:id_emp>/<int:mois>/<int:annee>/',bulletin_paie.index, name='bulletin_paie'),
    path('generate-journal_de_la_caisse/',journal_caisse.index, name='journal_caisse'),
    path('generate-rapports_du_stock/',rapports_du_stock.index, name='rapports_du_stock'),
    path('generate-historique_de_payement_accomodation/<int:num>/',recu_paiement.historique, name='historique_de_payement'),
    path('generate-facture_client_chambre/<int:num>/',recu_paiement.facture_client_chambre, name='facture_client_chambre'),
    path('generate-facture_client_chambre2/<int:num>/',recu_paiement.facture_client_chambre2, name='facture_client_chambre2'),
    
    
    path('predictor/',predictor.index, name='predictor'),
    path("get_avalable_modules/", views.get_avalable_modules, name="get_avalable_modules"),
    #FIN URLS ----------------------------------------------
    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)