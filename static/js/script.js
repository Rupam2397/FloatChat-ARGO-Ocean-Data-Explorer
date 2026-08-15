document.addEventListener("DOMContentLoaded", function () {

    const askButton = document.getElementById("askButton");
    const questionInput = document.getElementById("question");
    const resultContainer = document.getElementById("result");


    // Check elements
    if (!askButton || !questionInput || !resultContainer) {

        console.error("FloatChat elements not found.");

        return;
    }


    // Ask button
    askButton.addEventListener("click", askQuestion);


    // Press Enter
    questionInput.addEventListener("keypress", function (event) {

        if (event.key === "Enter") {

            askQuestion();

        }

    });


    async function askQuestion() {

        const question = questionInput.value.trim();


        if (!question) {

            resultContainer.innerHTML = `
                <p>
                    ⚠️ Please enter a question.
                </p>
            `;

            return;
        }


        // Loading message
        resultContainer.innerHTML = `
            <p>
                🔄 Analyzing ARGO ocean data...
            </p>
        `;


        try {

            const response = await fetch("/ask", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            });


            if (!response.ok) {

                throw new Error(
                    "Server returned status " + response.status
                );

            }


            const data = await response.json();


            console.log("FloatChat response:", data);


            if (!data.answer) {

                resultContainer.innerHTML = `
                    <div class="analysis-result">

                        <h3>⚠️ No Answer</h3>

                        <p>
                            The server did not return an answer.
                        </p>

                    </div>
                `;

                return;
            }


            // Display answer
            resultContainer.innerHTML = `
                <div class="analysis-result">

                    <h3>🤖 FloatChat Analysis</h3>

                    <p>
                        ${formatAnswer(data.answer)}
                    </p>

                </div>
            `;


        } catch (error) {

            console.error("FloatChat Error:", error);


            resultContainer.innerHTML = `
                <div class="analysis-result">

                    <h3>❌ Connection Error</h3>

                    <p>
                        Unable to connect to the FloatChat server.
                    </p>

                    <p>
                        Please make sure Flask is running.
                    </p>

                </div>
            `;

        }

    }


    function formatAnswer(answer) {

        return String(answer)
            .replace(/\n/g, "<br>")
            .replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );

    }

});
