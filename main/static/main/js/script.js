// const jobsData = [
//     { title: "Front-end Developer", description: "Описание вакансии для Front-end Developer.", salary: "50000", city: "City1", field: "IT" },
//     { title: "Back-end Developer", description: "Описание вакансии для Back-end Developer.", salary: "60000", city: "City2", field: "IT" },
//     { title: "UI/UX Designer", description: "Описание вакансии для UI/UX Designer.", salary: "55000", city: "City3", field: "Design" },
//     { title: "Project Manager", description: "Описание вакансии для Project Manager.", salary: "70000", city: "City4", field: "Management" },
//     { title: "Data Scientist", description: "Описание вакансии для Data Scientist.", salary: "80000", city: "City5", field: "Data Science" }
// ];

// function displayJobs(jobs = jobsData) {
//     const jobCardsContainer = document.getElementById("jobCards");
//     jobCardsContainer.innerHTML = "";

//     jobs.forEach((job, index) => {
//         const jobCard = document.createElement("div");
//         jobCard.className = "job-card";
//         jobCard.innerHTML = `
//             <h3>${job.title}</h3>
//             <p><strong>Salary:</strong> ${job.salary}</p>
//             <p><strong>City:</strong> ${job.city}</p>
//             <p><strong>Field:</strong> ${job.field}</p>
//             <p>${job.description.substring(0, 100)}...</p>
//             <button onclick="toggleDescription(${index})">Подробнее</button>
            
//             <!-- Expanded content and rating buttons -->
//             <div class="expanded-content" style="display: none;">
//                 <p>${job.description}</p>
//                 <button onclick="rateJob('INTERESTED', ${index})">Интересует</button>
//                 <button onclick="rateJob('NOT INTERESTED', ${index})">Не интересует</button>
//             </div>
//         `;
//         jobCardsContainer.appendChild(jobCard);
//     });
// }

// function toggleDescription(index) {
//     const expandedContent = document.querySelectorAll('.expanded-content');
//     expandedContent[index].style.display = expandedContent[index].style.display === 'none' ? 'block' : 'none';
// }

// function filterJobs() {
//     const salaryInput = document.getElementById("salaryInput").value.toLowerCase();
//     const cityInput = document.getElementById("cityInput").value.toLowerCase();
//     const fieldInput = document.getElementById("fieldInput").value.toLowerCase();

//     const filteredJobs = jobsData.filter(job =>
//         job.salary.toLowerCase().includes(salaryInput) &&
//         job.city.toLowerCase().includes(cityInput) &&
//         job.field.toLowerCase().includes(fieldInput)
//     );

//     displayJobs(filteredJobs);
// }

// function rateJob(status, index) {
//     console.log(`Job ${index + 1} is ${status}`);
// }

// displayJobs();