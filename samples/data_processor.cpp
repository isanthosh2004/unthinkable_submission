#include <iostream>
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
