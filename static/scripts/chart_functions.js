function getDay(){
    let curr = new Date();
    let today = curr.getDate();
    let date = new Date(curr.setDate(today)).toISOString().slice(0, 10);
    let hours = [];

    for (let i = 0; i <= 23; i++) {
        
        let hour = i;
        if (i < 10) {
            hour   =  "0" + hour;
        }
        hours.push(date + " " + hour + ":00:00");
    }
    return hours;
}

function getWeek(){
    let curr = new Date; 
    let week = [];

    for (let i = 1; i <= 7; i++) {
        let first = curr.getDate() - curr.getDay() + i; 
        let day = new Date(curr.setDate(first)).toISOString().slice(0, 10);
        week.push(day);
    }
    return week;
}

function getMonth(){
    let curr = new Date; 
    let DaysInMonth = new Date(curr.getFullYear(), curr.getMonth() + 1, 0).getDate();
    let month = [];

    for (let i = 1; i <= DaysInMonth; i++) {
        let day = new Date(curr.setDate(i)).toISOString().slice(0, 10);
        month.push(day);
    }
    return month;
}

function sumArray(arreglo){
    let total = 0;
    for(let i = 0; i < arreglo.length; i++){
        if(arreglo[i] != null){
            total = total + arreglo[i];
        }
        
    }

    return total;
}