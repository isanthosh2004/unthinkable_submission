"""
Demo script for Code Review Assistant
Creates sample code files for testing the application
"""

import os
from pathlib import Path

def create_sample_files():
    """Create sample code files for testing"""
    samples_dir = Path('samples')
    samples_dir.mkdir(exist_ok=True)
    
    # Sample Python file
    python_code = '''def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    try:
        num = int(input("Enter a number: "))
        result = calculate_fibonacci(num)
        print(f"Fibonacci({num}) = {result}")
    except ValueError:
        print("Please enter a valid number")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
'''
    
    with open(samples_dir / 'fibonacci.py', 'w') as f:
        f.write(python_code)
    
    # Sample JavaScript file
    js_code = '''function calculateFactorial(n) {
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
'''
    
    with open(samples_dir / 'factorial.js', 'w') as f:
        f.write(js_code)
    
    # Sample C++ file
    cpp_code = '''#include <iostream>
#include <vector>
#include <algorithm>

class DataProcessor {
private:
    std::vector<int> data;
    
public:
    void addData(int value) {
        data.push_back(value);
    }
    
    void sortData() {
        std::sort(data.begin(), data.end());
    }
    
    void printData() {
        for (const auto& value : data) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
    
    int getSum() {
        int sum = 0;
        for (const auto& value : data) {
            sum += value;
        }
        return sum;
    }
};

int main() {
    DataProcessor processor;
    
    // Add some sample data
    processor.addData(5);
    processor.addData(2);
    processor.addData(8);
    processor.addData(1);
    
    std::cout << "Original data: ";
    processor.printData();
    
    processor.sortData();
    std::cout << "Sorted data: ";
    processor.printData();
    
    std::cout << "Sum: " << processor.getSum() << std::endl;
    
    return 0;
}
'''
    
    with open(samples_dir / 'data_processor.cpp', 'w') as f:
        f.write(cpp_code)
    
    print("✅ Sample files created in 'samples/' directory:")
    print("   - fibonacci.py (Python)")
    print("   - factorial.js (JavaScript)")
    print("   - data_processor.cpp (C++)")
    print("\n📝 You can now upload these files in the Code Review Assistant!")

def main():
    """Main demo function"""
    print("🎯 Code Review Assistant - Demo Setup")
    print("=" * 50)
    
    create_sample_files()
    
    print("\n🚀 To test the application:")
    print("1. Make sure you have your OpenRouter API key in .env file")
    print("2. Run: streamlit run app.py")
    print("3. Upload the sample files from the 'samples/' directory")
    print("4. Click 'Start Code Review' to see the AI analysis")

if __name__ == "__main__":
    main()

