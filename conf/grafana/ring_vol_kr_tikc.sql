{
  "aliasColors": {},
  "cacheTimeout": null,
  "combine": {
    "label": "instrument",
    "threshold": ""
  },
  "datasource": "tick",
  "fontSize": "100%",
  "format": "short",
  "height": "",
  "id": 6,
  "interval": null,
  "legend": {
    "header": "",
    "percentage": true,
    "show": true,
    "sort": "current",
    "sortDesc": true,
    "values": true
  },
  "legendType": "Right side",
  "links": [],
  "maxDataPoints": 3,
  "nullPointMode": "connected",
  "pieType": "donut",
  "span": 8,
  "strokeWidth": "0",
  "targets": [
    {
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "instrument"
          ],
          "type": "tag"
        }
      ],
      "measurement": "tick",
      "orderByTime": "ASC",
      "policy": "tick_1d",
      "refId": "B",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "volume_today"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "last"
          }
        ]
      ],
      "tags": []
    }
  ],
  "title": "Volume Today",
  "transparent": true,
  "type": "grafana-piechart-panel",
  "valueName": "current"
}