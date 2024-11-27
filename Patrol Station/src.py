import random

#3shan ye-generate numbers le ay probability function given
class RandomGenerator:
   
    def __init__(self, values, probabilities):
        """
        Beyakhod elnumbers belprobabilities 
        ie: 0,1,2,3 | 0.17,0.23,0.25,0.35 -> 
        0    - 0.17 = 0, 
        0.17 - 0.4  = 1, 
        0.4  - 0.65 = 2, 
        0.65 - 1    = 3
        """ 
        #handle lw inputs ain't equal
        if len(values) != len(probabilities):
            print("Values and probabilities must have the same length.") 
        self.values = values
        self.probabilities = probabilities
        self.cumulative_probabilities = self._calculate_cumulative_probabilities()

    def _calculate_cumulative_probabilities(self):
        cumulative_probabilities = [] #array feh elcumulative probabilities 
        cumulative = 0 #start with zero
        for p in self.probabilities: #beyloop 3la kool elinputs 3shan yehseb elcumulative
            cumulative += p
            cumulative_probabilities.append(cumulative) #beyhot elcumulative to that point felarray
        return cumulative_probabilities

    def generate(self):
        random_number = random.random() #beyhseb random value
        for i, cp in enumerate(self.cumulative_probabilities): #byloop 3la kol random number(i) yeshofo hwa fe anhy range mn cp
            if random_number <= cp: 
                return self.values[i] 

        # Should never reach here if probabilities are well-formed
        raise ValueError("Error in cumulative probabilities.")

