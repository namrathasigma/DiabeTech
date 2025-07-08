class ContraindicationChecker:
    """
    A tool to check for absolute contraindications
    for proposed medications based on patient data.
    """

    def __init__(self):
        """
        Initializes the checker. Currently, it only for Metformin contraindications.
        """
        pass

    def check(self, egfr: int, proposed_medication: str) -> dict:
        """
        Checks a proposed medication against a patient's data for absolute contraindications.

        This function fulfills the requirements of the 'Contraindication Checker' component.
        For now, it only contains logic for Metformin.

        Args:
            egfr (int): The patient's estimated Glomerular Filtration Rate, a key
                        measure of kidney function.
            proposed_medication (str): The name of the medication to check.

        Returns:
            dict: A dictionary containing a boolean flag and a list of contraindication messages.
                  - 'is_safe' (bool): True if no contraindications are found, False otherwise.
                  - 'messages' (list): A list of strings, each describing a specific contraindication.
                                       The list is empty if the medication is safe.
        """
        # Standardize the medication name to lowercase for reliable checking.
        med_lower = proposed_medication.lower()

        # Initialize the output structure. The default assumption is that the medication is safe.
        output = {
            "is_safe": True,
            "messages": []
        }

        # --- Metformin Contraindication Check ---
        # This is the only absolute contraindication rule explicitly defined in Document 3.
        if med_lower == "metformin":
            # The rule from the 'MetforminProfile' is an eGFR < 30.
            if egfr < 30:
                output["is_safe"] = False
                output["messages"].append("Metformin is contraindicated in patients with an eGFR < 30 mL/min/1.73m² (severe CKD).")

        # If other medications are proposed, the function will return the default 'safe' output,
        # as no other absolute contraindication rules are defined in the knowledge base.

        return output