import pandas as pd
import numpy as np
import random
import csv
from pathlib import Path
from typing import List, Dict
import os

class BallotAssigner:
    """
    A class to assign ballots to verifiers from CSV and TXT files.
    """
    
    def __init__(self, ballots_csv_path: str = "ballot_ids.csv", verifiers_txt_path: str = "verifiers.txt"):
        """
        Initialize the BallotAssigner with file paths.
        
        Args:
            ballots_csv_path (str): Path to the CSV file containing ballot IDs
            verifiers_txt_path (str): Path to the TXT file containing verifier names
        """
        self.ballots_csv_path = ballots_csv_path
        self.verifiers_txt_path = verifiers_txt_path
        self.ballot_ids = []
        self.verifiers = []
        self.assignment_results = {}
        
        # Define the header structure
        self.header = [
            "id", "dominio", "unidad_educativa", "grado", "contador", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "21.1", "21.2", "21.3", "21.4", "21.5",
            "21.6", "21.7", "21.8", "21.9", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "31.1", "31.2",
            "31.3", "31.4", "31.5", "31.6", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44",
            "45", "46", "46.1", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61",
            "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
            "80", "81", "82", "83", "84", "85", "85.1", "85.2", "85.3", "85.4", "85.5", "85.6", "85.7", "85.8", "85.9",
            "85.10", "85.11", "85.12", "85.13", "86", "86.1", "86.2", "86.3", "86.4", "87", "87.1", "87.2", "87.3",
            "87.4", "88", "88.1", "88.2", "88.3", "88.4", "89", "89.1", "89.2", "89.3", "89.4", "90", "90.1", "90.2",
            "90.3", "90.4", "90.5", "90.6", "90.7", "90.8", "90.9", "90.10", "90.11", "90.12", "90.13", "90.14", "90.15",
            "90.16", "90.17", "90.18", "90.19", "91", "92", "93", "94", "95", "96", "97", "98", "98.1", "98.2", "98.3",
            "99", "100", "101", "102", "103", "103.1", "103.2", "104", "105", "106", "107", "108", "109", "110", "111",
            "112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122", "123", "124", "125", "126", "127",
            "128", "129", "129.1", "129.2", "129.3", "129.4", "129.5", "129.6", "129.7", "129.8", "129.9", "129.10"
        ]

    def load_data(self) -> None:
        """
        Load ballot IDs from CSV and verifier names from TXT file.
        """
        try:
            df = pd.read_csv(self.ballots_csv_path, header=None, names=['id'])
            self.ballot_ids = df['id'].tolist()
            print(f"Loaded {len(self.ballot_ids)} ballot IDs")
            
            with open(self.verifiers_txt_path, 'r', encoding='utf-8') as file:
                self.verifiers = [line.strip() for line in file if line.strip()]
            print(f"Loaded {len(self.verifiers)} verifiers")
            
        except FileNotFoundError as e:
            print(f"Error loading files: {e}")
            raise

    def assign_ballots(self, ballots_to_assign: int = 100) -> Dict[str, List[str]]:
        """
        Assign ballots to verifiers randomly.
        
        Args:
            ballots_to_assign (int): Number of ballots to assign
            
        Returns:
            Dict[str, List[str]]: Dictionary with verifier names as keys and assigned ballot IDs as values
        """
        if not self.ballot_ids or not self.verifiers:
            raise ValueError("No data loaded. Please call load_data() first.")
        if ballots_to_assign > len(self.ballot_ids):
            print(f"Warning: Requested {ballots_to_assign} ballots but only {len(self.ballot_ids)} available.")
            ballots_to_assign = len(self.ballot_ids)
        # Randomly select ballots
        selected_ballots = random.sample(self.ballot_ids, ballots_to_assign)
        
        # Calculate ballots per verifier
        ballots_per_verifier = ballots_to_assign // len(self.verifiers)
        remainder = ballots_to_assign % len(self.verifiers)

        # Assign ballots to verifiers
        random.shuffle(selected_ballots)
        assignment = {}

        start_index = 0
        for i, verifier in enumerate(self.verifiers):
            # Distribute remainder ballots among first few verifiers
            extra = 1 if i < remainder else 0
            end_index = start_index + ballots_per_verifier + extra
            
            assignment[verifier] = selected_ballots[start_index:end_index]
            start_index = end_index
        
        self.assignment_results = assignment
        return assignment
    
    def generate_csv_files(self, output_directory: str = "output") -> None:
        """
        Generate CSV files for each verifier with their assigned ballots.
        
        Args:
            output_directory (str): Directory where CSV files will be saved
        """
        if not self.assignment_results:
            raise ValueError("No assignments made. Please call assign_ballots() first.")
        os.makedirs(output_directory, exist_ok=True)        

        for verifier, ballots in self.assignment_results.items():
            # Create safe filename (remove special characters)
            safe_verifier_name = "Assigned_ballots_"+"".join(c for c in verifier if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{output_directory}/{safe_verifier_name}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                # Write header
                writer.writerow(self.header)
                # Write each ballot row
                for ballot_id in ballots:
                    row = [ballot_id] + ['0'] * (len(self.header) - 1)
                    writer.writerow(row)
            
            print(f"Generated CSV for {verifier}: {len(ballots)} ballots")
   
    def get_assignment_summary(self) -> pd.DataFrame:
        """
        Get a summary of the assignment distribution.
        
        Returns:
            pd.DataFrame: Summary dataframe with verifier names and ballot counts
        """
        summary_data = []
        for verifier, ballots in self.assignment_results.items():
            summary_data.append({
                'Verifier': verifier,
                'Ballots_Assigned': len(ballots),
                'Ballot_List': ', '.join(map(str, ballots))
            })
        
        return pd.DataFrame(summary_data)
    
    def run_complete_assignment(self, ballots_to_assign: int, output_directory: str = "output") -> None:
        """
        Complete workflow: load data, assign ballots, and generate CSV files.
        
        Args:
            ballots_to_assign (int): Number of ballots to assign
            output_directory (str): Directory where CSV files will be saved
        """
        print("Starting ballot assignment process...")
        self.load_data()
        self.assign_ballots(ballots_to_assign)
        self.generate_csv_files(output_directory)
        
        # Print summary
        summary = self.get_assignment_summary()
        print("\nAssignment Summary:")
        print(summary[['Verifier', 'Ballots_Assigned']].to_string(index=False))
        print(f"\nTotal ballots assigned: {summary['Ballots_Assigned'].sum()}")


# Example usage
if __name__ == "__main__":
    # Initialize the assigner
    assigner = BallotAssigner(
        ballots_csv_path="ballot_ids.csv",  # Replace with your CSV file path
        verifiers_txt_path="verifiers.txt"  # Replace with your TXT file path
    )
    
    assigner.run_complete_assignment(
        ballots_to_assign=50,  # Number of ballots to assign
        output_directory="verifier_csv_files"  # Output directory
    )