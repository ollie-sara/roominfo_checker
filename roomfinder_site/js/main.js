async function replaceTable() {
  var tds = $("#avail-table tbody").find("td");
  for (var i = 0; i < tds.length; i++) {
    if(tds[i].innerText == "1") {
      tds[i].innerText = "";
      tds[i].style.backgroundColor = "rgb(51, 202, 127)";
    } else if(tds[i].innerText == "0") {
      tds[i].innerText = "";
      tds[i].style.backgroundColor = "rgb(238, 56, 56)";
    }
  }
  return;
}

async function warnIfDead(lastChecked){
    var diff = new Date(((new Date()).getTime() + ((new Date()).getTimezoneOffset() * 60000) - lastChecked.getTime()) / (1000 * 60));
    if(diff > 45) {
      $("#oldDataWarning").html("⚠ Warning: The information on the site is more than <b>" + Math.round(diff) + " minutes</b> old. The automatic checker script might be down. Maybe Ollie hasn't noticed, you should contact him.");
      $("#oldDataWarning").show()
    }
}

async function fillOptions(){
  var jsonData = await (await fetch("/data/data.json")).json();
  console.log(jsonData);

  var all = $("<option>");
  all.attr("value", "0");
  all.text("All");
  $("#building").append(all);

  $.each(Object.keys(jsonData['buildings']), function (i, build) {
    var option = $("<option>");
    option.attr("value", "" + (i+1));
    option.text(build);
    $("#building").append(option);
  });

  var thisweek = new Date(jsonData['datetime_thisweek']);
  var nextweek = new Date(jsonData['datetime_nextweek']);

  const weekday = [
    "Mon, ",
    "Tue, ",
    "Wed, ",
    "Thu, ",
    "Fri, "
  ]

  for(var i = 0; i < 5; i++) {
    var option = $("<option>");
    option.attr("value", i);
    option.text(weekday[i] + thisweek.toLocaleDateString('de-CH'));
    $("#date").append(option);
    thisweek.setDate(thisweek.getDate() + 1);
    if(thisweek.getDate() == (new Date()).getDate()) {
      $("#date option:eq("+ i +")").prop("selected", true);
    }
  }

  for(var i = 0; i < 5; i++) {
    var option = $("<option>");
    option.attr("value", i+5);
    option.text(weekday[i] + nextweek.toLocaleDateString('de-CH'));
    $("#date").append(option);
    nextweek.setDate(nextweek.getDate() + 1);
  }
}

async function getData() {
  var jsonData = await (await fetch("/data/data.json")).json();
  var output = []

  var now = new Date(jsonData['datetime_now']);
  $("#updatedInfo").text("RoomInfo last checked: " + now.toLocaleString('de-CH'));
  warnIfDead(now);

  var date = $("#date").val();
  var week = Math.round(date / 5);
  date = date % 5;

  for(var i = 0; i < Object.keys(jsonData['buildings']).length; i++) {
    if(i != $("#building").val()-1 && $("#building").val() != 0) {
      continue;
    }
    for(var j = 0; j < Object.values(Object.values(jsonData['buildings'])[i]).length; j++) {
      var row = [];
      row.push(Object.keys(jsonData['buildings'])[i] + " " + Object.values(Object.values(jsonData['buildings'])[i])[j]['name']);
      row = row.concat(Object.values(Object.values(jsonData['buildings'])[i])[j][week == 0 ? "availability_thisweek" : "availability_nextweek"][date]);
      output.push(row);
    }
  }
  return output;
}

$(document).ready(async function(){
  var time_sel = $("#timerange_selection")
  var time = $("#timerange")

  time.slider({
    range: true,
    animate: "fast",
    min: 8,
    max: 20,
    values: [8, 20],
    slide: function(event, ui) {
      if(ui.values[0] == ui.values[1]) {
        if(ui.values[1] == 20) {
          ui.values[0]--;
        } else {
          ui.values[1]++;
        }
      }
      time_sel.text(ui.values[0] + ":00 - " + ui.values[1] + ":00");
    },
    change: async function(event, ui) {
      if(ui.values[0] == ui.values[1]) {
        if(ui.values[1] == 20) {
          ui.values[0]--;
        } else {
          ui.values[1]++;
        }
      }

      // Hide and Unhide
      var table = $("#avail-table").DataTable();
      var selector = [0];
      table.columns().visible(false);
      for(var i = 0; i < 12; i++) {
        if(i >= ui.values[0]-8 && i < ui.values[1]-8){
          selector = selector.concat([i*4+1, i*4+2, i*4+3, i*4+4]);
        }
      }
      table.columns(selector).visible(true);
      await replaceTable();
    }
  });

  time_sel.text(time.slider("values", 0) + ":00 - " + time.slider("values", 1) + ":00");

  await fillOptions();
  var data = await getData();
  $("#avail-table").dataTable({
    data: data,
    paging: false,
    searching: false,
    info: false,
    ordering: false
  });
  await replaceTable();

  $("#building").change(async function() {
    var newData = await getData();
    $("#avail-table").DataTable().clear().rows.add(newData).draw();
    await replaceTable();
  });

  $("#date").change(async function() {
    var newData = await getData();
    $("#avail-table").DataTable().clear().rows.add(newData).draw();
    await replaceTable();
  });
});
