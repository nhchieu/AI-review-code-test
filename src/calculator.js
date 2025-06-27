// Calculator class implementation with some intentional issues
class Calculator {
    constructor() {
        // Using var instead of let/const (issue)
        var result = 0;
        this.history = [];
    }

    // Missing parameter type validation (issue)
    add(a, b) {
        const result = a + b;
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }

    // Inconsistent method naming (issue)
    Subtract(a, b) {
        return a - b;
    }

    // Poor error handling (issue)
    divide(a, b) {
        if (b === 0) return null;  // Should throw error instead
        return a / b;
    }

    // Unnecessary complexity (issue)
    multiply(a, b) {
        let result = 0;
        for(let i = 0; i < Math.abs(b); i++) {
            result += Math.abs(a);
        }
        return (a < 0 && b > 0) || (a > 0 && b < 0) ? -result : result;
    }

    // Memory leak potential (issue)
    getHistory() {
        return this.history;  // Returning direct reference to internal array
    }

    // Magic number usage (issue)
    calculateDiscount(amount) {
        return amount * 0.85;  // Hard-coded discount value
    }
}

// Global variable usage (issue)
var globalCalculator = new Calculator();

// Export without proper module system (issue)
module.exports = Calculator; 