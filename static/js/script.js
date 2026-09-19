document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTS
    // =========================================================

    const askButton =
        document.getElementById("askButton");

    const questionInput =
        document.getElementById("question");

    const resultContainer =
        document.getElementById("result");

    const visualizationContainer =
        document.getElementById("visualization");

    const oceanDashboard =
        document.getElementById("oceanDashboard");

    const resultSourceBadge =
        document.getElementById("resultSourceBadge");

    const oceanPlace =
        document.getElementById("oceanPlace");

    const oceanCoordinates =
        document.getElementById("oceanCoordinates");

    const oceanTemperature =
        document.getElementById("oceanTemperature");

    const oceanSalinity =
        document.getElementById("oceanSalinity");

    const oceanCurrentSpeed =
        document.getElementById("oceanCurrentSpeed");

    const oceanCurrentDirection =
        document.getElementById("oceanCurrentDirection");

    const oceanDepth =
        document.getElementById("oceanDepth");

    const oceanTime =
        document.getElementById("oceanTime");

    const oceanMap =
        document.getElementById("oceanMap");

    // NEW ELEMENTS

    const oceanTemporalLabel =
        document.getElementById("oceanTemporalLabel");

    const oceanStatusLabel =
        document.getElementById("oceanStatusLabel");

    const oceanDataType =
        document.getElementById("oceanDataType");

    const oceanRequestedDate =
        document.getElementById("oceanRequestedDate");

    const oceanTemporalMode =
        document.getElementById("oceanTemporalMode");


    // =========================================================
    // CHECK REQUIRED ELEMENTS
    // =========================================================

    if (
        !askButton ||
        !questionInput ||
        !resultContainer ||
        !visualizationContainer
    ) {
        console.error(
            "FloatChat required HTML elements were not found."
        );

        return;
    }


    // =========================================================
    // ASK BUTTON
    // =========================================================

    askButton.addEventListener(
        "click",
        askQuestion
    );


    // =========================================================
    // ENTER KEY
    // =========================================================

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                askQuestion();
            }
        }
    );


    // =========================================================
    // QUICK EXAMPLE BUTTONS
    // =========================================================

    const exampleButtons =
        document.querySelectorAll(
            ".example-button"
        );


    exampleButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const question =
                        button.getAttribute(
                            "data-question"
                        );

                    if (question) {

                        questionInput.value =
                            question;

                        askQuestion();
                    }
                }
            );
        }
    );


    // =========================================================
    // ASK QUESTION
    // =========================================================

    async function askQuestion() {

        const question =
            questionInput.value.trim();


        // -----------------------------------------------------
        // EMPTY QUESTION
        // -----------------------------------------------------

        if (!question) {

            hideOceanDashboard();

            clearVisualization();

            setSourceBadge("", false);

            resultContainer.innerHTML = `
                <div class="analysis-result">
                    <p>
                        ⚠️ Please enter a question.
                    </p>
                </div>
            `;

            return;
        }


        // -----------------------------------------------------
        // LOADING
        // -----------------------------------------------------

        hideOceanDashboard();

        clearVisualization();

        setSourceBadge("", false);


        resultContainer.innerHTML = `
            <div class="loading-result">

                <div class="loading-spinner"></div>

                <p>
                    🌊 FloatChat is analyzing ocean data...
                </p>

                <p
                    style="
                        margin-top: 8px;
                        font-size: 13px;
                    "
                >
                    Global ocean requests may take
                    a few seconds.
                </p>

            </div>
        `;


        askButton.disabled = true;

        askButton.textContent =
            "Analyzing...";


        try {

            // =================================================
            // CALL FLASK
            // =================================================

            const response =
                await fetch(
                    "/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                question:
                                    question
                            })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Server returned status " +
                    response.status
                );
            }


            const data =
                await response.json();


            console.log(
                "FloatChat response:",
                data
            );


            // =================================================
            // NO ANSWER
            // =================================================

            if (!data.answer) {

                hideOceanDashboard();

                clearVisualization();

                resultContainer.innerHTML = `
                    <div class="analysis-result">

                        <h3>
                            ⚠️ No Answer
                        </h3>

                        <p>
                            The server did not return
                            an answer.
                        </p>

                    </div>
                `;

                return;
            }


            // =================================================
            // COMPLETE OCEAN CONDITIONS
            // =================================================

            if (
                data.type ===
                "ocean_conditions"
            ) {

                showOceanDashboard(
                    data,
                    question
                );

                return;
            }


            // =================================================
            // GLOBAL TEMPERATURE
            // =================================================

            if (
                data.type ===
                "ocean_temperature"
            ) {

                showSingleOceanResult(
                    data,
                    question
                );

                return;
            }


            // =================================================
            // GLOBAL SALINITY
            // =================================================

            if (
                data.type ===
                "ocean_salinity"
            ) {

                showSingleOceanResult(
                    data,
                    question
                );

                return;
            }


            // =================================================
            // GLOBAL CURRENT
            // =================================================

            if (
                data.type ===
                "ocean_current"
            ) {

                showSingleOceanResult(
                    data,
                    question
                );

                return;
            }


            // =================================================
            // ERROR RESPONSE
            // =================================================

            if (
                data.type ===
                "error"
            ) {

                hideOceanDashboard();

                clearVisualization();

                setSourceBadge("", false);


                resultContainer.innerHTML = `
                    <div class="error-result">
                        ${formatAnswer(
                            data.answer
                        )}
                    </div>
                `;

                return;
            }


            // =================================================
            // ARGO RESPONSE
            // =================================================

            hideOceanDashboard();


            setSourceBadge(
                "ARGO Observation Data",
                true
            );


            resultContainer.innerHTML = `
                <div class="analysis-result">

                    <h3>
                        🤖 FloatChat Analysis
                    </h3>

                    <p>
                        ${formatAnswer(
                            data.answer
                        )}
                    </p>

                </div>
            `;


            if (data.visualization) {

                createVisualization(
                    data
                );
            }

        } catch (error) {

            console.error(
                "FloatChat Error:",
                error
            );


            hideOceanDashboard();

            clearVisualization();

            setSourceBadge("", false);


            resultContainer.innerHTML = `
                <div class="error-result">

                    <strong>
                        ❌ Connection Error
                    </strong>

                    <br><br>

                    Unable to connect to the
                    FloatChat server.

                    <br><br>

                    Please make sure Flask is running.

                </div>
            `;

        } finally {

            askButton.disabled =
                false;

            askButton.textContent =
                "Ask";
        }
    }


    // =========================================================
    // TEMPORAL INFORMATION
    // =========================================================

    function getTemporalMode(data) {

        if (
            data.temporal_mode
        ) {

            return String(
                data.temporal_mode
            ).toLowerCase();
        }


        // -----------------------------------------------------
        // FALLBACK:
        // determine mode using requested/model date
        // -----------------------------------------------------

        const requested =
            getRequestedDate(data);


        if (!requested) {

            return "current";
        }


        const requestedDate =
            parseDateOnly(requested);


        if (!requestedDate) {

            return "current";
        }


        const today =
            new Date();


        const todayUTC =
            new Date(
                Date.UTC(
                    today.getUTCFullYear(),
                    today.getUTCMonth(),
                    today.getUTCDate()
                )
            );


        if (
            requestedDate.getTime() >
            todayUTC.getTime()
        ) {

            return "forecast";
        }


        if (
            requestedDate.getTime() <
            todayUTC.getTime()
        ) {

            return "past";
        }


        return "current";
    }


    // =========================================================
    // UPDATE TEMPORAL DASHBOARD
    // =========================================================

    function updateTemporalDashboard(
        data
    ) {

        const temporalMode =
            getTemporalMode(data);


        let temporalLabel =
            "Current Ocean Conditions";


        let statusLabel =
            "Operational Data";


        let dataType =
            "Operational Ocean Model";


        // -----------------------------------------------------
        // FORECAST
        // -----------------------------------------------------

        if (
            temporalMode ===
            "forecast"
        ) {

            temporalLabel =
                data.temporal_label ||
                "Ocean Forecast";

            statusLabel =
                "Operational Forecast";

            dataType =
                "Operational Forecast";
        }


        // -----------------------------------------------------
        // PAST
        // -----------------------------------------------------

        else if (
            temporalMode ===
            "past"
        ) {

            temporalLabel =
                data.temporal_label ||
                "Past Ocean Conditions";

            statusLabel =
                "Operational Analysis";

            dataType =
                "Operational Analysis";
        }


        // -----------------------------------------------------
        // CURRENT
        // -----------------------------------------------------

        else {

            temporalLabel =
                data.temporal_label ||
                "Current Ocean Conditions";

            statusLabel =
                "Operational Data";

            dataType =
                data.data_type ||
                "Operational Ocean Model";
        }


        // -----------------------------------------------------
        // TOP LABEL
        // -----------------------------------------------------

        if (oceanTemporalLabel) {

            oceanTemporalLabel.textContent =
                temporalLabel.toUpperCase();
        }


        // -----------------------------------------------------
        // STATUS
        // -----------------------------------------------------

        if (oceanStatusLabel) {

            oceanStatusLabel.textContent =
                statusLabel;
        }


        // -----------------------------------------------------
        // DATA TYPE
        // -----------------------------------------------------

        if (oceanDataType) {

            oceanDataType.textContent =
                dataType;
        }


        // -----------------------------------------------------
        // TEMPORAL MODE
        // -----------------------------------------------------

        if (oceanTemporalMode) {

            if (
                temporalMode ===
                "forecast"
            ) {

                oceanTemporalMode.textContent =
                    "Forecast";

            } else if (
                temporalMode ===
                "past"
            ) {

                oceanTemporalMode.textContent =
                    "Past / Analysis";

            } else {

                oceanTemporalMode.textContent =
                    "Current";
            }
        }
    }


    // =========================================================
    // COMPLETE OCEAN DASHBOARD
    // =========================================================

    function showOceanDashboard(
        data,
        originalQuestion
    ) {

        clearVisualization();


        if (!oceanDashboard) {

            console.error(
                "Ocean dashboard element not found."
            );

            return;
        }


        resultContainer.innerHTML =
            "";


        setSourceBadge(
            "Copernicus Marine",
            true
        );


        // =====================================================
        // CURRENT / PAST / FORECAST
        // =====================================================

        updateTemporalDashboard(
            data
        );


        // =====================================================
        // REQUESTED DATE
        // =====================================================

        const requestedDate =
            getRequestedDate(
                data
            );


        if (oceanRequestedDate) {

            oceanRequestedDate.textContent =
                formatRequestedDate(
                    requestedDate
                );
        }


        // =====================================================
        // LOCATION
        // =====================================================

        const location =
            data.location || {};


        const latitude =
            toNumber(
                location.latitude
            );


        const longitude =
            toNumber(
                location.longitude
            );


        const place =
            data.requested_place ||
            location.query ||
            getFriendlyPlaceName(
                originalQuestion,
                location
            );


        if (oceanPlace) {

            oceanPlace.textContent =
                place;
        }


        if (oceanCoordinates) {

            oceanCoordinates.textContent =
                formatCoordinates(
                    latitude,
                    longitude
                );
        }


        // =====================================================
        // TEMPERATURE
        // =====================================================

        if (
            oceanTemperature &&
            data.temperature &&
            data.temperature.success
        ) {

            oceanTemperature.textContent =
                data.temperature.value +
                " " +
                data.temperature.unit;

        } else if (
            oceanTemperature
        ) {

            oceanTemperature.textContent =
                "Unavailable";
        }


        // =====================================================
        // SALINITY
        // =====================================================

        if (
            oceanSalinity &&
            data.salinity &&
            data.salinity.success
        ) {

            oceanSalinity.textContent =
                data.salinity.value +
                " " +
                data.salinity.unit;

        } else if (
            oceanSalinity
        ) {

            oceanSalinity.textContent =
                "Unavailable";
        }


        // =====================================================
        // CURRENT SPEED + DIRECTION
        // =====================================================

        if (
            data.currents &&
            data.currents.success
        ) {

            if (oceanCurrentSpeed) {

                oceanCurrentSpeed.textContent =
                    data.currents.speed +
                    " " +
                    data.currents.speed_unit;
            }


            if (oceanCurrentDirection) {

                oceanCurrentDirection.textContent =
                    data.currents
                        .direction_degrees +
                    "° " +
                    data.currents.direction;
            }

        } else {

            if (oceanCurrentSpeed) {

                oceanCurrentSpeed.textContent =
                    "Unavailable";
            }


            if (oceanCurrentDirection) {

                oceanCurrentDirection.textContent =
                    "Unavailable";
            }
        }


        // =====================================================
        // MODEL DEPTH
        // =====================================================

        const gridDepth =
            getGridDepth(
                data
            );


        if (oceanDepth) {

            if (
                gridDepth !== null
            ) {

                oceanDepth.textContent =
                    gridDepth.toFixed(2) +
                    " m";

            } else {

                oceanDepth.textContent =
                    "--";
            }
        }


        // =====================================================
        // MODEL DATA TIME
        // =====================================================

        const dataTime =
            getOceanTime(
                data
            );


        if (oceanTime) {

            oceanTime.textContent =
                formatOceanTime(
                    dataTime
                );
        }


        // =====================================================
        // SHOW DASHBOARD
        // =====================================================

        oceanDashboard.style.display =
            "block";


        // =====================================================
        // MAP
        // =====================================================

        if (
            latitude !== null &&
            longitude !== null
        ) {

            createOceanMap(
                latitude,
                longitude,
                place
            );
        }
    }


    // =========================================================
    // SINGLE OCEAN RESULT
    // =========================================================

    function showSingleOceanResult(
        data,
        originalQuestion
    ) {

        hideOceanDashboard();

        clearVisualization();


        setSourceBadge(
            "Copernicus Marine",
            true
        );


        const temporalMode =
            getTemporalMode(
                data
            );


        let title =
            "🌊 Current Ocean Conditions";


        if (
            temporalMode ===
            "forecast"
        ) {

            title =
                "🔮 Ocean Forecast";

        } else if (
            temporalMode ===
            "past"
        ) {

            title =
                "🕘 Past Ocean Conditions";
        }


        resultContainer.innerHTML = `
            <div class="analysis-result">

                <h3>
                    ${escapeHtml(title)}
                </h3>

                <p>
                    ${formatAnswer(
                        data.answer
                    )}
                </p>

            </div>
        `;


        const location =
            data.location || {};


        const latitude =
            toNumber(
                location.latitude
            );


        const longitude =
            toNumber(
                location.longitude
            );


        const place =
            data.requested_place ||
            location.query ||
            getFriendlyPlaceName(
                originalQuestion,
                location
            );


        if (
            latitude !== null &&
            longitude !== null
        ) {

            createGlobalMapInVisualization(
                latitude,
                longitude,
                place
            );
        }
    }


    // =========================================================
    // GET REQUESTED DATE
    // =========================================================

    function getRequestedDate(
        data
    ) {

        // Top-level value from Flask
        if (
            data.requested_date
        ) {

            return data.requested_date;
        }


        if (
            data.requested_time
        ) {

            return data.requested_time;
        }


        // Temperature
        if (
            data.temperature &&
            data.temperature.requested_time
        ) {

            return data.temperature
                .requested_time;
        }


        // Salinity
        if (
            data.salinity &&
            data.salinity.requested_time
        ) {

            return data.salinity
                .requested_time;
        }


        // Currents
        if (
            data.currents &&
            data.currents.requested_time
        ) {

            return data.currents
                .requested_time;
        }


        return null;
    }


    // =========================================================
    // PARSE DATE ONLY
    // =========================================================

    function parseDateOnly(
        value
    ) {

        if (!value) {

            return null;
        }


        const text =
            String(value);


        const match =
            text.match(
                /^(\d{4})-(\d{2})-(\d{2})/
            );


        if (!match) {

            return null;
        }


        const year =
            Number(match[1]);

        const month =
            Number(match[2]);

        const day =
            Number(match[3]);


        const date =
            new Date(
                Date.UTC(
                    year,
                    month - 1,
                    day
                )
            );


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return null;
        }


        return date;
    }


    // =========================================================
    // FORMAT REQUESTED DATE
    // =========================================================

    function formatRequestedDate(
        value
    ) {

        if (!value) {

            return "--";
        }


        const date =
            parseDateOnly(
                value
            );


        if (!date) {

            return String(
                value
            );
        }


        return date.toLocaleDateString(
            "en-GB",
            {
                day:
                    "2-digit",

                month:
                    "short",

                year:
                    "numeric",

                timeZone:
                    "UTC"
            }
        );
    }


    // =========================================================
    // FRIENDLY PLACE NAME
    // =========================================================

    function getFriendlyPlaceName(
        question,
        location
    ) {

        const patterns = [

            /\bnear\s+(.+)$/i,

            /\bin\s+(.+)$/i,

            /\baround\s+(.+)$/i,

            /\bat\s+(.+)$/i,

            /\bof\s+(.+)$/i,

            /\bfor\s+(.+)$/i
        ];


        for (
            const pattern
            of patterns
        ) {

            const match =
                question.match(
                    pattern
                );


            if (
                match &&
                match[1]
            ) {

                let place =
                    match[1].trim();


                // REMOVE DEPTH

                place =
                    place.replace(
                        /\s+at\s+\d+(?:\.\d+)?\s*(?:m|meter|meters).*$/i,
                        ""
                    );


                // REMOVE TIME WORDS

                place =
                    place.replace(
                        /\b(today|now|currently|latest|current|tomorrow|yesterday|tonight)\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\bright\s+now\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\bthis\s+(morning|afternoon|evening)\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\b(next|last)\s+(day|week|month)\b/gi,
                        ""
                    );


                // RELATIVE DATE EXPRESSIONS

                place =
                    place.replace(
                        /\bin\s+\d+\s+days?\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\bnext\s+\d+\s+days?\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\blast\s+\d+\s+days?\b/gi,
                        ""
                    );


                place =
                    place.replace(
                        /\b\d+\s+days?\s+ago\b/gi,
                        ""
                    );


                // YYYY-MM-DD

                place =
                    place.replace(
                        /\bon\s+\d{4}-\d{2}-\d{2}\b/gi,
                        ""
                    );


                // DD/MM/YYYY

                place =
                    place.replace(
                        /\bon\s+\d{1,2}[/-]\d{1,2}[/-]\d{4}\b/gi,
                        ""
                    );


                // CLEAN

                place =
                    place.replace(
                        /[?.!,]+$/g,
                        ""
                    );


                place =
                    place.replace(
                        /\s+/g,
                        " "
                    );


                place =
                    place.trim();


                if (place) {

                    return capitalizeWords(
                        place
                    );
                }
            }
        }


        if (
            location &&
            location.query
        ) {

            return location.query;
        }


        if (
            location &&
            location.display_name
        ) {

            return location.display_name;
        }


        return "Ocean Location";
    }


    // =========================================================
    // CAPITALIZE
    // =========================================================

    function capitalizeWords(
        text
    ) {

        return String(text)

            .split(" ")

            .map(
                function (word) {

                    if (!word) {

                        return word;
                    }


                    return (
                        word
                            .charAt(0)
                            .toUpperCase()
                        +
                        word.slice(1)
                    );
                }
            )

            .join(" ");
    }


    // =========================================================
    // FORMAT COORDINATES
    // =========================================================

    function formatCoordinates(
        latitude,
        longitude
    ) {

        if (
            latitude === null ||
            longitude === null
        ) {

            return "--";
        }


        const latDirection =
            latitude >= 0
                ? "N"
                : "S";


        const lonDirection =
            longitude >= 0
                ? "E"
                : "W";


        return (
            Math.abs(latitude)
                .toFixed(4)
            +
            "° "
            +
            latDirection
            +
            " • "
            +
            Math.abs(longitude)
                .toFixed(4)
            +
            "° "
            +
            lonDirection
        );
    }


    // =========================================================
    // FORMAT MODEL DATA TIME
    // =========================================================

    function formatOceanTime(
        value
    ) {

        if (!value) {

            return "--";
        }


        const text =
            String(value);


        const normalized =
            text.replace(
                /(\.\d{3})\d+/,
                "$1"
            );


        let dateText =
            normalized;


        if (
            !dateText.endsWith("Z")
        ) {

            dateText += "Z";
        }


        const date =
            new Date(
                dateText
            );


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return text;
        }


        return date.toLocaleString(
            "en-GB",
            {
                day:
                    "2-digit",

                month:
                    "short",

                year:
                    "numeric",

                hour:
                    "2-digit",

                minute:
                    "2-digit",

                timeZone:
                    "UTC",

                timeZoneName:
                    "short"
            }
        );
    }


    // =========================================================
    // GET MODEL DATA TIME
    // =========================================================

    function getOceanTime(
        data
    ) {

        if (
            data.temperature &&
            data.temperature.success
        ) {

            return data.temperature.time;
        }


        if (
            data.salinity &&
            data.salinity.success
        ) {

            return data.salinity.time;
        }


        if (
            data.currents &&
            data.currents.success
        ) {

            return data.currents.time;
        }


        return null;
    }


    // =========================================================
    // GET ACTUAL GRID DEPTH
    // =========================================================

    function getGridDepth(
        data
    ) {

        const possibleResults = [

            data.temperature,

            data.salinity,

            data.currents
        ];


        for (
            const result
            of possibleResults
        ) {

            if (
                result &&
                result.success &&
                result.actual_grid_location
            ) {

                const depth =
                    toNumber(
                        result
                            .actual_grid_location
                            .depth
                    );


                if (
                    depth !== null
                ) {

                    return depth;
                }
            }
        }


        return null;
    }


    // =========================================================
    // SAFE NUMBER
    // =========================================================

    function toNumber(
        value
    ) {

        const number =
            Number(value);


        if (
            Number.isFinite(
                number
            )
        ) {

            return number;
        }


        return null;
    }


    // =========================================================
    // OCEAN MAP
    // =========================================================

    function createOceanMap(
        latitude,
        longitude,
        place
    ) {

        if (
            !oceanMap ||
            typeof Plotly ===
            "undefined"
        ) {

            return;
        }


        try {

            Plotly.purge(
                oceanMap
            );

        } catch (error) {

            console.debug(
                error
            );
        }


        const trace = {

            type:
                "scattergeo",

            mode:
                "markers+text",

            lat:
                [latitude],

            lon:
                [longitude],

            text:
                [place],

            textposition:
                "top center",

            marker: {

                size:
                    13,

                line: {

                    width:
                        1
                }
            },

            hovertemplate:
                "<b>" +
                escapeHtml(place) +
                "</b><br>" +
                "Latitude: " +
                latitude.toFixed(4) +
                "°<br>" +
                "Longitude: " +
                longitude.toFixed(4) +
                "°<extra></extra>"
        };


        const layout = {

            title: {

                text:
                    "Global Ocean Query Location"
            },

            geo: {

                projection: {

                    type:
                        "natural earth"
                },

                showland:
                    true,

                showcountries:
                    true,

                showocean:
                    true,

                showcoastlines:
                    true,

                center: {

                    lat:
                        latitude,

                    lon:
                        longitude
                },

                projection_scale:
                    3.2
            },

            margin: {

                t:
                    60,

                r:
                    20,

                b:
                    20,

                l:
                    20
            }
        };


        Plotly.newPlot(
            oceanMap,
            [trace],
            layout,
            {
                responsive:
                    true,

                displaylogo:
                    false
            }
        );
    }


    // =========================================================
    // SINGLE RESULT MAP
    // =========================================================

    function createGlobalMapInVisualization(
        latitude,
        longitude,
        place
    ) {

        if (
            typeof Plotly ===
            "undefined"
        ) {

            return;
        }


        const trace = {

            type:
                "scattergeo",

            mode:
                "markers+text",

            lat:
                [latitude],

            lon:
                [longitude],

            text:
                [place],

            textposition:
                "top center",

            marker: {

                size:
                    13
            },

            hovertemplate:
                "<b>" +
                escapeHtml(place) +
                "</b><br>" +
                "Latitude: " +
                latitude.toFixed(4) +
                "°<br>" +
                "Longitude: " +
                longitude.toFixed(4) +
                "°<extra></extra>"
        };


        const layout = {

            title: {

                text:
                    "Ocean Query Location"
            },

            geo: {

                projection: {

                    type:
                        "natural earth"
                },

                showland:
                    true,

                showcountries:
                    true,

                showocean:
                    true,

                showcoastlines:
                    true,

                center: {

                    lat:
                        latitude,

                    lon:
                        longitude
                },

                projection_scale:
                    3
            },

            margin: {

                t:
                    60,

                r:
                    20,

                b:
                    20,

                l:
                    20
            }
        };


        Plotly.newPlot(
            visualizationContainer,
            [trace],
            layout,
            {
                responsive:
                    true,

                displaylogo:
                    false
            }
        );
    }


    // =========================================================
    // ARGO VISUALIZATIONS
    // =========================================================

    function createVisualization(
        data
    ) {

        clearVisualization();


        // =====================================================
        // TEMPERATURE
        // =====================================================

        if (
            data.type ===
            "temperature" &&
            data.visualization &&
            data.visualization.temperature &&
            data.visualization.pressure
        ) {

            const trace = {

                x:
                    data.visualization
                        .temperature,

                y:
                    data.visualization
                        .pressure,

                mode:
                    "markers",

                type:
                    "scatter",

                marker: {

                    size:
                        6,

                    opacity:
                        0.7
                },

                name:
                    "Temperature"
            };


            const layout = {

                title: {

                    text:
                        "ARGO Temperature vs Pressure"
                },

                xaxis: {

                    title: {

                        text:
                            "Temperature (°C)"
                    }
                },

                yaxis: {

                    title: {

                        text:
                            "Pressure (dbar)"
                    },

                    autorange:
                        "reversed"
                },

                hovermode:
                    "closest",

                margin: {

                    t:
                        60,

                    r:
                        30,

                    b:
                        70,

                    l:
                        80
                }
            };


            Plotly.newPlot(
                visualizationContainer,
                [trace],
                layout,
                {
                    responsive:
                        true,

                    displaylogo:
                        false
                }
            );
        }


        // =====================================================
        // SALINITY
        // =====================================================

        else if (
            data.type ===
            "salinity" &&
            data.visualization &&
            data.visualization.salinity &&
            data.visualization.pressure
        ) {

            const trace = {

                x:
                    data.visualization
                        .salinity,

                y:
                    data.visualization
                        .pressure,

                mode:
                    "markers",

                type:
                    "scatter",

                marker: {

                    size:
                        6,

                    opacity:
                        0.7
                },

                name:
                    "Salinity"
            };


            const layout = {

                title: {

                    text:
                        "ARGO Salinity vs Pressure"
                },

                xaxis: {

                    title: {

                        text:
                            "Salinity (PSU)"
                    }
                },

                yaxis: {

                    title: {

                        text:
                            "Pressure (dbar)"
                    },

                    autorange:
                        "reversed"
                },

                hovermode:
                    "closest",

                margin: {

                    t:
                        60,

                    r:
                        30,

                    b:
                        70,

                    l:
                        80
                }
            };


            Plotly.newPlot(
                visualizationContainer,
                [trace],
                layout,
                {
                    responsive:
                        true,

                    displaylogo:
                        false
                }
            );
        }


        // =====================================================
        // ARGO LOCATION MAP
        // =====================================================

        else if (
            data.type ===
            "location" &&
            data.visualization &&
            data.visualization.latitude &&
            data.visualization.longitude
        ) {

            const trace = {

                type:
                    "scattergeo",

                mode:
                    "markers",

                lat:
                    data.visualization
                        .latitude,

                lon:
                    data.visualization
                        .longitude,

                marker: {

                    size:
                        6,

                    opacity:
                        0.7
                },

                name:
                    "ARGO Observations"
            };


            const layout = {

                title: {

                    text:
                        "ARGO Geographic Coverage"
                },

                geo: {

                    projection: {

                        type:
                            "natural earth"
                    },

                    showland:
                        true,

                    showcountries:
                        true,

                    showocean:
                        true,

                    lataxis: {

                        range:
                            [-15, 25]
                    },

                    lonaxis: {

                        range:
                            [55, 95]
                    }
                },

                margin: {

                    t:
                        60,

                    r:
                        20,

                    b:
                        20,

                    l:
                        20
                }
            };


            Plotly.newPlot(
                visualizationContainer,
                [trace],
                layout,
                {
                    responsive:
                        true,

                    displaylogo:
                        false
                }
            );
        }
    }


    // =========================================================
    // HIDE DASHBOARD
    // =========================================================

    function hideOceanDashboard() {

        if (oceanDashboard) {

            oceanDashboard.style.display =
                "none";
        }


        if (
            oceanMap &&
            typeof Plotly !==
            "undefined"
        ) {

            try {

                Plotly.purge(
                    oceanMap
                );

            } catch (error) {

                console.debug(
                    "Ocean map clear:",
                    error
                );
            }
        }
    }


    // =========================================================
    // SOURCE BADGE
    // =========================================================

    function setSourceBadge(
        text,
        visible
    ) {

        if (!resultSourceBadge) {

            return;
        }


        if (
            visible &&
            text
        ) {

            resultSourceBadge.textContent =
                text;

            resultSourceBadge.style.display =
                "inline-block";

        } else {

            resultSourceBadge.textContent =
                "";

            resultSourceBadge.style.display =
                "none";
        }
    }


    // =========================================================
    // CLEAR VISUALIZATION
    // =========================================================

    function clearVisualization() {

        if (
            typeof Plotly !==
            "undefined"
        ) {

            try {

                Plotly.purge(
                    visualizationContainer
                );

            } catch (error) {

                console.debug(
                    "Visualization clear:",
                    error
                );
            }
        }


        visualizationContainer.innerHTML =
            "";
    }


    // =========================================================
    // FORMAT ANSWER
    // =========================================================

    function formatAnswer(
        answer
    ) {

        return escapeHtml(
            String(answer)
        )
            .replace(
                /\n/g,
                "<br>"
            )
            .replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );
    }


    // =========================================================
    // HTML SAFETY
    // =========================================================

    function escapeHtml(
        value
    ) {

        return String(value)

            .replace(
                /&/g,
                "&amp;"
            )

            .replace(
                /</g,
                "&lt;"
            )

            .replace(
                />/g,
                "&gt;"
            )

            .replace(
                /"/g,
                "&quot;"
            )

            .replace(
                /'/g,
                "&#039;"
            );
    }

});