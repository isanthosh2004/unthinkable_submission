function calculateFactorial(n) {
    if (n < 0) {
        throw new Error("Factorial is not defined for negative numbers");
    }
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * calculateFactorial(n - 1);
}

function validateInput(input) {
    const num = parseInt(input);
    if (isNaN(num)) {
        throw new Error("Invalid input: not a number");
    }
    return num;
}

// Main execution
try {
    const userInput = prompt("Enter a number:");
    const number = validateInput(userInput);
    const result = calculateFactorial(number);
    console.log(`Factorial of ${number} is ${result}`);
} catch (error) {
    console.error("Error:", error.message);
}
