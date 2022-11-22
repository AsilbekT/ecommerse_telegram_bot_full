const bodyContent = document.getElementById("body-content");
// const btn1 = document.getElementById("btn1");
// const btn2 = document.getElementById("btn2");

function playSound(url) {
    const audio = new Audio(url);
    audio.play();
}

const playAudio = document.getElementById("playSoundBtn")
// const playSound = document.getElementById("playSound")

playAudio.addEventListener("click", () => {
    playSound("https://ansorfamily.uz/zakaz/audio/audio2.mp3");
})

src = "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
integrity = "sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
crossorigin = "anonymous"

const firebaseConfig = {
    apiKey: "AIzaSyAMUkqFby32pmMWxpc352RNOPmcfOIkHMg",
    authDomain: "ansor-7a46e.firebaseapp.com",
    databaseURL: "https://ansor-7a46e-default-rtdb.firebaseio.com",
    projectId: "ansor-7a46e",
    storageBucket: "ansor-7a46e.appspot.com",
    messagingSenderId: "715329180131",
    appId: "1:715329180131:web:de176a010ec97a89cf50d6",
    measurementId: "G-9MYPLZKKCG"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();

var starCountRef = firebase.database().ref("orders");
// console.log(starCountRef)
starCountRef.on("value", (snapshot) => {
    let arrayOfTable = []
    const data = snapshot.val();
    let keys = Object.keys(data);
    let last_key = keys.slice(-1)

    // for (let i = 0; i < keys.length; i++) {
    //     console.log(keys[i])
    // }
    playSound("https://ansorfamily.uz/zakaz/audio/audio2.mp3");

    keys.slice().reverse().forEach((key) => {
        const singleData = data[key];
        arrayOfTable.push(
            `<tr>
            <div class="diver">
                <td>No</td>
                <td>${singleData['id']}</td>
                <td>${singleData['fio']}</td>
                <td>${singleData['total_amount']}</td>
                <td>${singleData['selected_location']}</td>
                <td>${singleData['location']}</td>
                <td>${singleData['order_type']}</td>
                <td>${singleData['phone']}</td>
                <td>${singleData['name']}</td>
                <td>${singleData['time']}</td>
                <td>${singleData['user_feedback']}</td>
                <td><button 
                    data-all=${key}
                    data-buttonType="tastiqlash"
                    data-orderId=${singleData.id}
                    data-userName=${singleData.fio}
                    data-totalAmount=${singleData.total_amount}
                    data-meals=${singleData.name}
                type='button' class='specialBtn btn' id='btn2'>Принимать заказ</button>
                <button 
                    data-all=${key}
                    data-buttonType="yetqazib_berildi"
                    data-orderId=${singleData.id}
                    data-userName=${singleData.fio}
                    data-totalAmount=${singleData.total_amount}
                    data-meals=${singleData.name}
                class="specialBtn btn"  id="btn2" style="margin-top: 10px" "> Доставленно </button>
                </td>
            </div>
            </tr>
            `
        );
    })
    bodyContent.innerHTML = arrayOfTable;

    const arrayOfButtons = document.querySelectorAll('.specialBtn');
    for (let index = 0; index < arrayOfButtons.length; index++) {
        const element = arrayOfButtons[index];
        element.addEventListener("click", fetchData)
    }
});


function fetchData(selected_data) {
    let all_data = selected_data.target.getAttribute("data-all")
    let button_type = selected_data.target.getAttribute("data-buttonType")
    let order_id = selected_data.target.getAttribute("data-orderId")
    let username = selected_data.target.getAttribute("data-userName")
    let totalAmount = selected_data.target.getAttribute("data-totalAmount")
    let meals = selected_data.target.getAttribute("data-meals")
    let selected_data_to_send = {
        "all_data": all_data,
        "button_type": button_type,
        "order_id": order_id,
        "username": username,
        "total_amount": totalAmount,
        "meals": meals,
    };
    fetch("https://ansorfamily.uz/receive", {
        method: "POST", // or 'PUT'
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(selected_data_to_send),
    })

};

