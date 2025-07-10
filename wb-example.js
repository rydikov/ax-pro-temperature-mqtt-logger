var cells = {
    temperature: {
      title: "Температура",
      type: "value",
      units: "deg C",
      value: 0
    },
    charge_value: {
      title: "Процент заряда",
      type: "value",
      units: "%",
      value: 0,
    },
    status: {
      title: "Статус",
      type: "text",
      value: ""
    },
  };

var devices = [
  {id: 'ax-pro-1', title: 'Датчик 1', humidity: true},
  {id: 'ax-pro-2', title: 'Датчик 2', humidity: true},
  {id: 'ax-pro-3', title: 'Датчик 3'},
  {id: 'ax-pro-4', title: 'Датчик 4'},
  {id: 'ax-pro-5', title: 'Датчик 5'},
  {id: 'ax-pro-6', title: 'Датчик 6'},
  {id: 'ax-pro-7', title: 'Датчик 7'},
  {id: 'ax-pro-8', title: 'Датчик 8'},
  {id: 'ax-pro-9', title: 'Датчик 9'},
];

for (var i = 0; i < devices.length; i++) {
  var d = devices[i];
  var v_dev = defineVirtualDevice(d.id, {
    title: d.title,
    cells: cells
  });
  if (d.humidity !== undefined){
    v_dev.addControl("humidity", {
      title: "Влажность",
      type: "value",
      units: "%, RH",
      value: 0,
      max: 100,
      min: 1
    });  
  }
};

// Sync with virtual device
trackMqtt("ax-pro/sensors/#", function(message) {

  var value = JSON.parse(message.value);
  log.debug(message.topic);

  var parts = message.topic.split("/");
  var sensorId = parts[2];  // sensor_id
  var devName = 'ax-pro-' + sensorId;

  var device = getDevice(devName);
  
  if (device !== undefined) {
    dev[devName + '/' + 'temperature'] = value['temperature'];
    dev[devName + '/' + 'charge_value'] = 'chargeValue' in value ? value['chargeValue'] : 0;
    dev[devName + '/' + 'status'] = value['status'];
    if (device.isControlExists('humidity')) {
      dev[devName + '/' + 'humidity'] = 'humidity' in value ? value['humidity'] : 0;
    };
  }

});