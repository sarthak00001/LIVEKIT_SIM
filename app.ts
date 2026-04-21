// app.ts
// A simple function to add two numbers
function addNumbers(a: number, b: number): number {
    return a + b;
}

// Defining variables with strict types
let num1: number = 5;
let num2: number = 10;

// Call the function and output the result
const result: number = addNumbers(num1, num2);
console.log(`The sum of ${num1} and ${num2} is: ${result}`);
