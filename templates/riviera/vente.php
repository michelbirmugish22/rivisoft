{% load static %}

<!-- NAVIGATIONS  -->

  <main id="main" class="main">

    <div class="pagetitle">
      <h1>Nouvelle vente</h1>
      <nav>
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="index.html">Accueil</a></li>
          <li class="breadcrumb-item">Mise à jour</li>
          <li class="breadcrumb-item active">Vente</li>
        </ol>
      </nav>
    </div><!-- End Page Title -->
    <section class="section">
      <div class="row">

        <div class="col-lg-8">

          <div class="card">
            <div class="card-body">
              <h5 class="card-title"></h5>

              <!-- Floating Labels Form -->
              <form action="./backend/gest-vente/ajouter.php" method="post" class="row g-3 form-vente">
                <div class="row div-ligne-vente">
                <div class="col-md-6">
                  <div class="form-floating">
                    <input type="date" class="form-control" id="date_ven" name="date_ven" placeholder="" required>
                    <label for="floatingName">Date de vente</label>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-floating">
                    <select name="id_client" id="id_client" class="form-select" placeholder="" required>
                        <option value=""></option>
                      <?php $req = $conn->query("SELECT * FROM client ORDER BY nom_cli");?>
                      <?php while ($row=$req->fetch_assoc()):?>
                      <option value="<?=$row["id_cli"]?>"><?=$row["nom_cli"]." ".$row["postnom_cli"]?></option>
                      <?php endwhile;?>
                    </select>
                    <label for="">Client</label>
                  </div>
                </div>
                <?php include("lignes-ventes.php"); ?>
                </div>
                <div class="col-md-6">
                    <button type="button" class="btn btn-primary ajouter-vente"><i class="bi bi-plus"></i></button>
                    <button type="submit" data-bs-toggle="modal" class="btn btn-primary">Enregistrer</button>
                    <button type="reset" class="btn btn-danger">Reset</button>
                </div>
                <div class="form-check form-switch col-md-6">
                  <input class="form-check-input" type="checkbox" name="f_payee" id="flexSwitchCheckDefault">
                  <label class="form-check-label" for="flexSwitchCheckDefault">Facture PAYEE CASH en totalité.</label>
                </div>
                
                <div class="text-center">
                  
                </div>
              </form>
              <!-- End floating Labels Form -->
                <hr>

            </div>
          </div>

        </div>

        <div class="col-lg-4">

          <div class="card">
            <div class="card-body">
              <h1 class="card-title">Prévisualisation</h1>
              <table class="table table-bordered" style="font-size:10px;">
              
              <thead>
                <tr>
                    <th colspan="5">
                        <span id="nom_ven_tab">Client : AMANI KULIMUSHI</span>
                        <p id="date_ven_tab">Date   : Le 12/12/2024</p>
                        <h6 id="fact_ven_tab">Facture N° : .............. / 2023 </h6>
                    </th>
                </tr>
                <tr>
                    <th>Code</th>
                    <th>Produit</th>
                    <th>Qté</th>
                    <th>PU</th>
                    <th>PT</th>
                </tr>
                </thead>
                <tbody class="forme-facture">

                </tbody>
                <tr>
                    <th colspan="4">TOTAL TTC</th>
                    <th id="tot">0</th>
                </tr>
              </table>
            </div>
          </div>

        </div>
      </div>
    </section>

  </main><!-- End #main -->
<div class="modal fade" id="message_modal" tabindex="1">
  <div class="modal-dialog modal-dialog-centered modal-md">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title msg_title">Confirmation</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body text-danger msg_info">
        Voulez-vous effectuer cette action ?.
      </div>
      <div class="modal-footer">
        <!-- <button type="button" class="btn btn-danger" data-bs-dismiss="modal">Non</button> -->
        <button type="button" data-bs-dismiss="modal" class="btn btn-primary">Fermer</button>
      </div>
    </div>
  </div>
</div><!-- End Vertically centered Modal-->
  <?php include("foot.php");?>

<script>
  $("#date_ven").val(new Date().toLocaleDateString())
  // Au chargement de la page, initialiser le message
  const message = $("#ajouter_img");
  message.text("Ajouter une photo du produit");
  $("#div-photo_art").hide()
  // Écouter l'événement `change` de l'élément `input`
  $("#flexSwitchCheckDefault").on("change", () => {
    // Récupérer la valeur de l'élément `input`
    const value = $("#flexSwitchCheckDefault").prop("checked");

    // Afficher le message approprié
    if (value) {
      $("#div-photo_art").show()
    } else {
        $("#div-photo_art").hide()
    }
  });

$(document).ready(function () {
    for (let i = 2; i <=20; i++) {
        $(".section_produit"+i).hide();
        $(".section_qte"+i).hide();
    }
    
});

  $(".ajouter-vente").on("click", function () {
    var min=2000

    // ici je trouve le minimum des controls cashés
    for (let i = 1; i <=20; i++){
        if($(".section_produit"+i).is(":hidden") && parseInt($("#p"+i).val())<min){
            min=parseInt($("#p"+i).val());
        }
    }
    if(parseFloat($("#qte_ven"+(min-1)).val()) > parseFloat($("#qte_prod"+(min-1)).val())){
      $(".msg_info").text("La qté demandé n'est pas disponible. Il ne reste que "+$("#qte_prod"+(min-1)).val()+ " pièces en stock.")
      $(".msg_title").text("Stock insuffisant")
      $("#message_modal").modal("show")
      $("#qte_ven"+(min-1)).css("background-color","red");
      $("#qte_ven"+(min-1)).css("color","white");
    }
    else{
      $("#qte_ven"+(min-1)).css("background-color","white");
      $("#qte_ven"+(min-1)).css("color","black");

      if($.trim($("#qte_ven"+(min-1)).val()).length>0){
        $(".section_produit"+min).show();
        $(".section_qte"+min).show();
        add_tab(min-1)
      }else{
        alert("La Quantité ne peut pas être vide.")
      }
    }
  });

i=0;
function add_tab(id){
    i+=1;
    var id_prod = $("#id_prod"+id).val();
    var qte_ven = $("#qte_ven"+id).val();
    var pt =qte_ven*$("#id_prod"+id+" option:selected").data("pu")
    pt =Math.round(pt*100)/100
    var ligne = `
    <tr>
        <td id="id">${i}</td>
        <td id="prod">${$("#id_prod"+id+" option:selected").text()}</td>
        <td id="qte">${qte_ven}</td>
        <td id="pu">${Math.round($("#id_prod"+id+" option:selected").data("pu")*100)/100}</td>
        <td id="pt">${pt}</td>
    </tr>
    `
    tot = parseFloat($("#tot").text())+pt
    $("#tot").text(tot)
    $(".forme-facture").append(ligne)
}


//Quand on sélectionne le client et la date
$("#id_client").on("change", function () {
    $("#nom_ven_tab").text("Client : "+$("#id_client option:selected").text())
});
$("#date_ven").on("change", function () {
    $("#date_ven_tab").text("Date : "+$("#date_ven").val())
});
</script>

<script>
$(".enre").on("click", function (e) {
    e.preventDefault()
    alert("OK")
});
</script>

<!--    -->
<script>
for (let i = 1; i <= 20; i++) {
  $("#id_prod"+i).on("change", function () {
    
    $("#qte_prod"+i).val($("#id_prod"+i+" option:selected").data("qte"))
    $("#pv_prod"+i).val($("#id_prod"+i+" option:selected").data("pu"))
});
}
</script>

<script>
  //Extration des variables dans l'url
  const url = new URL(window.location.href);
  const params = url.searchParams;
  const msg=params.get('msg');
  $(document).ready(function () {
  if(msg){
  $(".msg_title").text("Success");
  $(".msg_info").html(`<center><img src="./images/succes.png" alt="" style="width:50px;height:auto;padding-right:1px;">  Vente effectuée.</center>`);
  $("#message_modal").modal("show");
  }
  });
</script>

<script>
for(let i=0;i<=20;i++){
  $(".section_produit"+i).on("change", function(){
    $(".info_qte"+i).text("Qté : "+$("#id_prod"+i+" option:selected").data("qte")+" [PV: "+$("#id_prod"+i+" option:selected").data("pu")+" u.m]")
  })
}
</script>