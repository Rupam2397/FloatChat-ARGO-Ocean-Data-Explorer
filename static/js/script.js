document.addEventListener(
    "DOMContentLoaded",
    function () {


        const askButton =
            document.getElementById(
                "askButton"
            );


        const questionInput =
            document.getElementById(
                "question"
            );


        const resultContainer =
            document.getElementById(
                "result"
            );


        const visualizationContainer =
            document.getElementById(
                "visualization"
            );


        // ==========================================
        // CHECK ELEMENTS
        // ==========================================

        if (
            !askButton ||
            !questionInput ||
            !resultContainer ||
            !visualizationContainer
        ) {

            console.error(
                "FloatChat elements not found."
            );

            return;
        }


        // ==========================================
        // ASK BUTTON
        // ==========================================

        askButton.addEventListener(
            "click",
            askQuestion
        );


        // ==========================================
        // ENTER KEY
        // ==========================================

        questionInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    askQuestion();

                }

            }
        );


        // ==========================================
        // ASK QUESTION
        // ==========================================

        async function askQuestion() {


            const question =
                questionInput
                    .value
                    .trim();


            // Empty question
            if (!question) {

                resultContainer.innerHTML = `
                    <div class="analysis-result">

                        <p>
                            ⚠️ Please enter a question.
                        </p>

                    </div>
                `;

                clearVisualization();

                return;
            }


            // Loading
            resultContainer.innerHTML = `
                <div class="analysis-result">

                    <p>
                        🔄 Analyzing ARGO ocean data...
                    </p>

                </div>
            `;


            clearVisualization();


            try {


                // ==================================
                // SEND QUESTION TO FLASK
                // ==================================

                const response =
                    await fetch(
                        "/ask",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify(
                                    {
                                        question:
                                            question
                                    }
                                )

                        }
                    );


                // Server error
                if (!response.ok) {

                    throw new Error(
                        "Server returned status " +
                        response.status
                    );

                }


                // Convert response to JSON
                const data =
                    await response.json();


                console.log(
                    "FloatChat response:",
                    data
                );


                // ==================================
                // CHECK ANSWER
                // ==================================

                if (!data.answer) {

                    resultContainer.innerHTML = `
                        <div class="analysis-result">

                            <h3>
                                ⚠️ No Answer
                            </h3>

                            <p>
                                The server did not
                                return an answer.
                            </p>

                        </div>
                    `;

                    return;
                }


                // ==================================
                // DISPLAY ANSWER
                // ==================================

                resultContainer.innerHTML = `
                    <div class="analysis-result">

                        <h3>
                            🤖 FloatChat Analysis
                        </h3>

                        <p>
                            ${formatAnswer(data.answer)}
                        </p>

                    </div>
                `;


                // ==================================
                // CREATE VISUALIZATION
                // ==================================

                if (
                    data.visualization
                ) {

                    createVisualization(
                        data
                    );

                }


            }
            catch (error) {


                console.error(
                    "FloatChat Error:",
                    error
                );


                resultContainer.innerHTML = `
                    <div class="analysis-result">

                        <h3>
                            ❌ Connection Error
                        </h3>

                        <p>
                            Unable to connect to
                            the FloatChat server.
                        </p>

                        <p>
                            Please make sure
                            Flask is running.
                        </p>

                    </div>
                `;


                clearVisualization();

            }

        }


        // ==========================================
        // CREATE VISUALIZATION
        // ==========================================

        function createVisualization(
            data
        ) {


            clearVisualization();


            // ======================================
            // TEMPERATURE VS PRESSURE
            // ======================================

            if (
                data.type ===
                    "temperature"
                &&
                data.visualization
                    .temperature
                &&
                data.visualization
                    .pressure
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

                        size: 6,

                        opacity: 0.7

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

                        t: 60,

                        r: 30,

                        b: 70,

                        l: 80

                    }

                };


                Plotly.newPlot(

                    visualizationContainer,

                    [trace],

                    layout,

                    {
                        responsive: true,
                        displaylogo: false
                    }

                );

            }


            // ======================================
            // SALINITY VS PRESSURE
            // ======================================

            else if (
                data.type ===
                    "salinity"
                &&
                data.visualization
                    .salinity
                &&
                data.visualization
                    .pressure
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

                        size: 6,

                        opacity: 0.7

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
                                "Salinity"
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

                        t: 60,

                        r: 30,

                        b: 70,

                        l: 80

                    }

                };


                Plotly.newPlot(

                    visualizationContainer,

                    [trace],

                    layout,

                    {
                        responsive: true,
                        displaylogo: false
                    }

                );

            }


            // ======================================
            // ARGO LOCATION MAP
            // ======================================

            else if (
                data.type ===
                    "location"
                &&
                data.visualization
                    .latitude
                &&
                data.visualization
                    .longitude
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

                        size: 6,

                        opacity: 0.7

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

                        t: 60,

                        r: 20,

                        b: 20,

                        l: 20

                    }

                };


                Plotly.newPlot(

                    visualizationContainer,

                    [trace],

                    layout,

                    {
                        responsive: true,
                        displaylogo: false
                    }

                );

            }

        }


        // ==========================================
        // CLEAR VISUALIZATION
        // ==========================================

        function clearVisualization() {


            if (
                typeof Plotly !==
                "undefined"
            ) {

                Plotly.purge(
                    visualizationContainer
                );

            }


            visualizationContainer.innerHTML =
                "";

        }


        // ==========================================
        // FORMAT ANSWER
        // ==========================================

        function formatAnswer(
            answer
        ) {


            return String(answer)

                .replace(
                    /\n/g,
                    "<br>"
                )

                .replace(
                    /\*\*(.*?)\*\*/g,
                    "<strong>$1</strong>"
                );

        }


    }
);