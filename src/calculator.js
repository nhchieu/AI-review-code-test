// Calculator class implementation with various issues for testing
class Calculator {
    constructor() {
        // Using var instead of let/const (issue)
        var result = 0;
        this.history = [];
        // Magic numbers (issue)
        this.MAX_HISTORY = 1000;
        this.TAX_RATE = 0.1;
        // Global variable leak (issue)
        window.calculatorInstance = this;
    }

    // Missing parameter type validation and using async without await (issues)
    async add(a, b) {
        const result = a + b;
        this._addToHistory(`${a} + ${b} = ${result}`);
        return result;
    }

    // Inconsistent method naming and unnecessary complexity (issues)
    MULTIPLY(a, b) {
        var result = 0;
        // Potential infinite loop (issue)
        while(result < a * b) {
            result += a;
        }
        return result;
    }

    // SQL Injection vulnerability simulation (security issue)
    async getUserCalculations(userId) {
        // This is just for demonstration
        const query = `SELECT * FROM calculations WHERE user_id = ${userId}`;
        return await this.executeQuery(query);
    }

    // Memory leak and performance issue
    calculateBatch(numbers) {
        // Creating large arrays in memory
        let results = [];
        for(let i = 0; i < numbers.length; i++) {
            // Inefficient array manipulation
            results = [...results, numbers[i] * 2];
            
            // Memory leak - storing all intermediate results
            this.history.push(results.slice());
        }
        return results;
    }

    // Race condition potential and no error handling
    async saveResult(result) {
        // Direct database call without error handling
        await this.db.save(result);
        
        // Race condition potential
        this.lastResult = result;
        this.resultCount++;
    }

    // Hardcoded credentials (security issue)
    connectToDatabase() {
        const dbConfig = {
            host: 'localhost',
            user: 'admin',
            password: 'password123',
            database: 'calculator_db'
        };
        // Using credentials directly in code
        return this.createConnection(dbConfig);
    }

    // XSS vulnerability simulation
    displayResult(result) {
        // Directly inserting user input into HTML
        document.getElementById('result').innerHTML = result;
    }

    // Private method with improper implementation
    _addToHistory(entry) {
        // No limit check could lead to memory issues
        this.history.push(entry);
        
        // Synchronous file write could block main thread
        this.saveToFile(entry);
    }
}

// Global variable and singleton pattern misuse
var globalCalculator = new Calculator();

// Export without proper module system
module.exports = Calculator;

// Dead code
function unusedFunction() {
    console.log("This function is never called");
}

// Memory leak through event listener
document.addEventListener('calculate', function(e) {
    // This listener is never removed
    globalCalculator.add(e.a, e.b);
}); 