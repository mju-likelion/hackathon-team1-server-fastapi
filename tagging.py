import pandas as pd
import re

# Dictionary for company name variations
company_names_extended = {
    "DB Insurance": ["DB", "DB Insurance"],
    "MG Insurance": ["MG", "MG Insurance"],
    "Kyobo Life Insurance": ["Kyobo Life", "Kyobo", "Kyobo's"],
    "Nonghyup Non-Life Insurance": ["Nonghyup Non-Life", "Nonghyup", "Nonghyup's"],
    "Nonghyup Life Insurance": ["Nonghyup Life", "Nonghyup", "Nonghyup's"],
    "Dongyang Life Insurance": ["Dongyang Life", "Dongyang", "Dongyang's"],
    "Lotte Non-Life Insurance": ["Lotte Non-Life", "Lotte", "Lotte's"],
    "Meritz Fire & Marine Insurance": ["Meritz Fire & Marine", "Meritz", "Meritz's"],
    "Samsung Life Insurance": ["Samsung Life", "Samsung", "Samsung's"],
    "Samsung Fire & Marine Insurance": [
        "Samsung Fire & Marine",
        "Samsung",
        "Samsung's",
    ],
    "Hanwha Non-Life Insuranace": ["Hanwha Non-Life", "Hanwha", "Hanwha's"],
    "Hanwha Life Insurance": ["Hanwha Life", "Hanwha", "Hanwha's"],
    "Hyundai Marine & Fire Insurance": [
        "Hyundai Marine & Fire",
        "Hyundai",
        "Hyundai's",
        "the modern sea",
    ],
    "Heungkuk Life Insurance": ["Heungkuk Life", "Heungkuk", "Heungkuk's"],
    "Heungkuk Fire & Marine Insurance": [
        "Heungkuk Fire & Marine",
        "Heungkuk",
        "Heungkuk's",
    ],
}

insuranceType_list = [
    "medical-free",
    "no medical history",
    "disease-free",
    "healthcare-free",
    "higher risk of getting sick",
    "sick person",
    "health problems",
    "past illnesses."
    "previous medical conditions."
    "history of diseases."
    "history of health issues."
    "previous illnesses."
    "history of health problems."
    "history of past diseases."
    "health issues in the past."
    "suffered from diseases.",
]


# Convert tags to BIOES format
def convert_to_bioes(tags):
    new_tags = []
    n = len(tags)
    for idx, tag in enumerate(tags):
        if tag == "O":
            new_tags.append(tag)
        else:
            if "-" not in tag:  # If single word entity
                new_tags.append("S-" + tag.split("-")[1])
            else:
                prefix, label = tag.split("-")
                if idx == 0:
                    if (
                        idx + 1 < n
                        and tags[idx + 1].split("-")[1] == label
                        and tags[idx + 1].split("-")[0] != "B"
                    ):
                        new_tags.append("B-" + label)
                    else:
                        new_tags.append("S-" + label)
                elif idx == n - 1:
                    if tags[idx - 1].split("-")[-1] == label:
                        new_tags.append("E-" + label)
                    else:
                        new_tags.append("S-" + label)
                else:
                    if (
                        tags[idx - 1].split("-")[-1] == label
                        and tags[idx + 1].split("-")[-1] == label
                    ):
                        new_tags.append("I-" + label)
                    elif tags[idx - 1].split("-")[-1] == label:
                        new_tags.append("E-" + label)
                    elif idx + 1 < n and tags[idx + 1].split("-")[1] == label:
                        new_tags.append("B-" + label)
                    else:
                        new_tags.append("S-" + label)
    return new_tags


# Correcting the error and completing the bioes_tagging function


def bioes_tagging(question):
    words = question.split()
    tags = ["O"] * len(words)

    for idx, word in enumerate(words):
        # Check for company names
        for _, variations in company_names_extended.items():
            for variation in variations:
                for match in re.finditer(
                    r"\b" + re.escape(variation) + r"\b", question
                ):
                    start, end = match.span()
                    start_idx = len(question[:start].split()) - 1
                    end_idx = len(question[:end].split()) - 1
                    if start_idx == end_idx:
                        tags[start_idx] = "E-companyName"
                    else:
                        tags[start_idx] = "B-companyName"
                        tags[start_idx + 1 : end_idx] = ["I-companyName"] * (
                            end_idx - start_idx - 1
                        )
                        tags[end_idx] = "E-companyName"

        # Check for insuranceType
        if word in insuranceType_list:
            tags[idx] = "E-insuranceType"

        if word in ["sick", "disease-prone", "health-free", "sick person"]:
            tags[idx] = "B-insuranceType"
            if idx + 1 < len(words) and words[idx + 1] == "person":
                tags[idx + 1] = "E-insuranceType"

        # Check for Gender
        genders = ["male", "man", "men's", "his", "female", "woman", "women", "her"]
        for gender in genders:
            if gender in word:
                tags[idx] = "E-Gender"

        # Check for Age
        age_pattern = re.compile(
            r"^[1-9]\d{0,1}$|^[1-9]\d{0,1}-year(?:s)?-old$|\d{1,2}th year|\d{1,2}s"
        )
        if age_pattern.match(word) or re.match(r"^\d{1,2}0s$", word):
            tags[idx] = "S-Age"

        price_pattern = re.compile(
            r"^\d{1,5}(?:,\d{3})*$|^\d{1,5}(?:,\d{3})*\s*won$|^\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*won$"
        )
        if price_pattern.match(word):
            tags[idx] = "E-insurancePrice"
            if idx > 0 and words[idx - 1].isdigit():
                tags[idx - 1 : idx + 1] = ["B-insurancePrice", "E-insurancePrice"]

        numeric_value = re.sub(
            r"\D", "", word
        )  # Remove non-numeric characters for easy comparison
        if numeric_value:
            if int(numeric_value) <= 100:
                tags[idx] = "S-Age"

            elif int(numeric_value) >= 1000:
                tags[idx] = "E-insurancePrice"

        price_range_types = [
            "more cheap",
            "or less",
            "or over",
            "over",
            "less",
            "around",
            "below",
            "under",
            "less than",
        ]

        # for price_type in price_range_types:
        for price_type in price_range_types:
            for match in re.finditer(r"\b" + re.escape(price_type) + r"\b", question):
                start, end = match.span()
                start_idx = len(question[:start].split()) - 1
                end_idx = len(question[:end].split()) - 1
                if start_idx == end_idx:
                    tags[start_idx] = "E-insurancePriceRange"
                else:
                    tags[start_idx] = "B-insurancePriceRange"
                    tags[start_idx + 1 : end_idx] = ["I-insurancePriceRange"] * (
                        end_idx - start_idx - 1
                    )
                    tags[end_idx] = "E-insurancePriceRange"

        minmax_price_types = [
            "most expensive",
            "very expensive",
            "most affordable",
            "cheapest",
            "mid-range",
            "luxurious",
            "economical",
        ]
        for minmax_price_type in minmax_price_types:
            pass
            for match in re.finditer(
                r"\b" + re.escape(minmax_price_type) + r"\b", question
            ):
                start, end = match.span()
                start_idx = len(question[:start].split()) - 1
                end_idx = len(question[:end].split()) - 1
                if start_idx == end_idx:
                    tags[start_idx] = "E-minmaxInsurancePriceRange"
                else:
                    tags[start_idx] = "B-minmaxInsurancePriceRange"
                    tags[start_idx + 1 : end_idx + 1] = [
                        "I-minmaxInsurancePriceRange"
                    ] * (end_idx - start_idx)
                    tags[end_idx] = "E-minmaxInsurancePriceRange"

        # Check for cancellationRefund
        if word in ["refundable", "refund"]:
            tags[idx] = "E-cancellationRefund"

        # Check for registrationType
        registration_types = [
            "consultation-free",
            "online-registration",
            "in-person visit",
            "mail-in application",
            "Agent-assisted",
            "Agent assisted",
            "agent assisted",
            "Phone Enrollment",
            "phone enrollment",
        ]
        for reg_type in registration_types:
            if reg_type in " ".join(words[idx : idx + len(reg_type.split())]):
                for j in range(len(reg_type.split())):
                    tags[idx + j] = "E-registrationType"

        # Additional regular expressions for more coverage
        pattern = r"^\d{2,3}(?:,\d{3})*\.\d{1,2}$"
        if re.match(pattern, word):
            # For price formats like 1,234.56 or .56
            tags[idx] = "E-priceIndex"

    return tags
