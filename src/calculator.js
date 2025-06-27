// Calculator class implementation with some intentional issues
class Calculator {
    constructor() {
        // Using var instead of let/const (issue)
        var result = 0;
        this.history = [];
        // Magic numbers (issue)
        this.MAX_HISTORY = 1000;
        this.TAX_RATE = 0.1;
    }

    // Missing parameter type validation (issue)
    add(a, b) {
        const result = a + b;
        this._addToHistory(`${a} + ${b} = ${result}`); // Using private method naming but not truly private
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

    // New method with security issue
    calculateTax(income, userInput) {
        // Security issue: eval usage
        const taxRate = eval(userInput) || this.TAX_RATE;
        return income * taxRate;
    }

    // New method with performance issue
    findInHistory(query) {
        // Performance issue: Creating new array on each call
        const reversedHistory = this.history.slice().reverse();
        // Inefficient search
        return reversedHistory.filter(item => item.includes(query));
    }

    // Private method but not using proper private field syntax
    _addToHistory(entry) {
        // Race condition potential
        if (this.history.length >= this.MAX_HISTORY) {
            this.history.shift();
        }
        this.history.push(entry);
    }

    // Method with multiple responsibilities (violating Single Responsibility Principle)
    processTransaction(amount, type, discount, tax) {
        let result = amount;
        
        if (discount) {
            result = this.calculateDiscount(result);
        }
        
        if (tax) {
            result = result + this.calculateTax(result, '0.1');
        }
        
        // Side effect: Logging to console
        console.log(`Processing ${type} transaction: ${amount} -> ${result}`);
        
        return result;
    }
}

// Global variable usage (issue)
var globalCalculator = new Calculator();

// Export without proper module system (issue)
module.exports = Calculator; 