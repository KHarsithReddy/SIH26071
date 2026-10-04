// =====================================================
// SIH26071 - Heavy Rainfall & Flood Risk GIS
// GIS MAP MODULE
// =====================================================


// =====================================================
// 1. CREATE MAP
// =====================================================

const map = L.map("map").setView([22.5, 79.0], 5);


// =====================================================
// 2. OPENSTREETMAP BASE MAP
// =====================================================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// =====================================================
// 3. GIS PREDICTION DATA
// =====================================================
//
// This contains temporary testing data.
//
// Later, your teammate can replace this using:
//
// updateGIS(predictions);
//
// Example:
//
// updateGIS({
//     "Telangana": {
//         risk: "High",
//         confidence: 91
//     }
// });
//
// =====================================================

let stateRiskData = {

    "Telangana": {
        risk: "High",
        confidence: 91
    },

    "Andhra Pradesh": {
        risk: "Moderate",
        confidence: 84
    },

    "Karnataka": {
        risk: "Low",
        confidence: 78
    },

    "Kerala": {
        risk: "High",
        confidence: 89
    },

    "Maharashtra": {
        risk: "Moderate",
        confidence: 82
    },

    "Odisha": {
        risk: "High",
        confidence: 94
    }

};


// =====================================================
// 4. STORE GEOJSON LAYER
// =====================================================

let indiaStatesLayer = null;


// =====================================================
// 5. GET RISK COLOR
// =====================================================

function getRiskColor(risk) {

    if (!risk) {
        return "#9ca3af";
    }

    const normalizedRisk =
        String(risk).toLowerCase();


    if (
        normalizedRisk === "high" ||
        normalizedRisk === "severe flood risk" ||
        normalizedRisk === "severe"
    ) {
        return "#ef4444";
    }


    if (
        normalizedRisk === "moderate" ||
        normalizedRisk === "moderate risk"
    ) {
        return "#f59e0b";
    }


    if (
        normalizedRisk === "low" ||
        normalizedRisk === "low risk"
    ) {
        return "#22c55e";
    }


    return "#9ca3af";
}


// =====================================================
// 6. DEFAULT STATE STYLE
// =====================================================

function defaultStyle() {

    return {

        color: "#374151",

        weight: 1,

        fillColor: "#d1d5db",

        fillOpacity: 0.45

    };

}


// =====================================================
// 7. GET STATE STYLE
// =====================================================

function getStateStyle(stateName) {

    const data =
        stateRiskData[stateName];


    if (!data) {

        return defaultStyle();

    }


    return {

        color: "#374151",

        weight: 1,

        fillColor:
            getRiskColor(data.risk),

        fillOpacity: 0.65

    };

}


// =====================================================
// 8. HIGHLIGHT STATE
// =====================================================

function highlightState(event) {

    const layer = event.target;


    layer.setStyle({

        weight: 3,

        color: "#111827",

        fillOpacity: 0.8

    });


    layer.bringToFront();

}


// =====================================================
// 9. RESET STATE
// =====================================================

function resetState(event) {

    const layer = event.target;


    const stateName =
        layer.feature.properties.name;


    layer.setStyle(
        getStateStyle(stateName)
    );

}


// =====================================================
// 10. DISPLAY STATE DETAILS
// =====================================================

function displayStateDetails(
    stateName,
    data
) {

    const details =
        document.getElementById(
            "stateDetails"
        );


    if (!data) {

        details.innerHTML = `

            <h3>${stateName}</h3>

            <p>
                No prediction available yet.
            </p>

        `;

        return;

    }


    details.innerHTML = `

        <h3>${stateName}</h3>

        <p>
            <strong>Flood Risk:</strong>
            ${data.risk}
        </p>

        <p>
            <strong>Confidence:</strong>
            ${data.confidence}%
        </p>

    `;

}


// =====================================================
// 11. STATE CLICK
// =====================================================

function stateClicked(event) {

    const layer = event.target;


    const stateName =
        layer.feature.properties.name;


    const data =
        stateRiskData[stateName];


    // Update selected state

    const selectedState =
        document.getElementById(
            "selectedState"
        );


    selectedState.textContent =
        stateName;


    // Update sidebar

    displayStateDetails(
        stateName,
        data
    );


    // =================================================
    // STATE HAS PREDICTION
    // =================================================

    if (data) {

        layer.bindPopup(`

            <div>

                <h3>${stateName}</h3>

                <p>
                    <strong>Flood Risk:</strong>
                    ${data.risk}
                </p>

                <p>
                    <strong>Confidence:</strong>
                    ${data.confidence}%
                </p>

            </div>

        `).openPopup();

    }


    // =================================================
    // STATE DOES NOT HAVE PREDICTION
    // =================================================

    else {

        layer.bindPopup(`

            <div>

                <h3>${stateName}</h3>

                <p>
                    No prediction available yet.
                </p>

            </div>

        `).openPopup();

    }

}


// =====================================================
// 12. STYLE GEOJSON STATE
// =====================================================

function styleState(feature) {

    const stateName =
        feature.properties.name;


    return getStateStyle(
        stateName
    );

}


// =====================================================
// 13. GEOJSON EVENTS
// =====================================================

function onEachState(
    feature,
    layer
) {

    const stateName =
        feature.properties.name;


    layer.on({

        mouseover:
            highlightState,

        mouseout:
            resetState,

        click:
            stateClicked

    });


    layer.bindTooltip(
        stateName
    );

}


// =====================================================
// 14. UPDATE GIS
// =====================================================
//
// THIS IS THE MAIN FUNCTION YOUR TEAMMATE WILL USE.
//
// Example:
//
// updateGIS({
//     "Telangana": {
//         risk: "High",
//         confidence: 92
//     },
//
//     "Andhra Pradesh": {
//         risk: "Moderate",
//         confidence: 76
//     }
// });
//
// =====================================================

function updateGIS(predictions) {

    console.log(
        "Updating GIS with predictions:",
        predictions
    );


    // Safety check

    if (
        !predictions ||
        typeof predictions !== "object"
    ) {

        console.error(
            "updateGIS() expected an object containing state predictions."
        );

        return;

    }


    // Replace current prediction data

    stateRiskData =
        predictions;


    // Update all states on the map

    if (indiaStatesLayer) {

        indiaStatesLayer.eachLayer(
            function(layer) {

                const stateName =
                    layer.feature.properties.name;


                layer.setStyle(
                    getStateStyle(stateName)
                );

            }
        );

    }


    console.log(
        "GIS updated successfully."
    );

}


// =====================================================
// 15. MAKE updateGIS AVAILABLE TO OTHER FILES
// =====================================================
//
// This allows your teammate's frontend JavaScript
// to call:
//
// updateGIS(predictions);
//
// =====================================================

window.updateGIS =
    updateGIS;


// =====================================================
// 16. LOAD INDIAN STATES GEOJSON
// =====================================================

fetch(
    "data/indian-states.geojson"
)

    .then(
        function(response) {

            if (!response.ok) {

                throw new Error(
                    "Could not load Indian states GeoJSON"
                );

            }


            return response.json();

        }
    )

    .then(
        function(data) {

            // Create the GeoJSON layer

            indiaStatesLayer =
                L.geoJSON(
                    data,
                    {

                        style:
                            styleState,

                        onEachFeature:
                            onEachState

                    }
                );


            // Add layer to map

            indiaStatesLayer.addTo(map);


            console.log(
                "Indian states GeoJSON loaded successfully."
            );

        }
    )

    .catch(
        function(error) {

            console.error(
                "GIS Error:",
                error
            );


            alert(
                "Unable to load the India state map."
            );

        }
    );