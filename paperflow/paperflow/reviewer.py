"""
Reviewer class for expertise matching, conflict detection, and assignment optimization.
Implements algorithms for fair and effective reviewer-paper matching.
"""

from datetime import datetime


class Reviewer:
    """
    Represents a peer reviewer with expertise matching and assignment capabilities.

    Attributes:
        name (str): Reviewer's full name.
        email (str): Reviewer's email address.
        expertise_areas (list): Areas of expertise as keyword strings.
        affiliation (str): Reviewer's institution.
        max_reviews (int): Maximum number of reviews this reviewer can handle.
        current_assignments (list): List of currently assigned paper IDs.
    """

    def __init__(self, name, email, expertise_areas=None, affiliation='',
                 max_reviews=5):
        """
        Initialize a Reviewer instance.

        Args:
            name (str): Reviewer's full name.
            email (str): Email address.
            expertise_areas (list): List of expertise keyword strings.
            affiliation (str): Institutional affiliation.
            max_reviews (int): Maximum concurrent review assignments.
        """
        self.name = name
        self.email = email
        self.expertise_areas = [e.lower().strip() for e in (expertise_areas or [])]
        self.affiliation = affiliation
        self.max_reviews = max_reviews
        self.current_assignments = []
        self.completed_reviews = []
        self.created_at = datetime.utcnow()

    def calculate_expertise_match(self, paper_keywords):
        """
        Calculate a match score between reviewer expertise and paper keywords.
        Uses Jaccard-like similarity with partial matching support.

        Args:
            paper_keywords (list): Keywords from the paper.

        Returns:
            float: Match score between 0.0 and 1.0.
        """
        if not self.expertise_areas or not paper_keywords:
            return 0.0

        paper_kw = {k.lower().strip() for k in paper_keywords}
        expert_kw = set(self.expertise_areas)

        # Exact match count
        exact_matches = len(paper_kw & expert_kw)

        # Partial match: check if any expert keyword is a substring of paper keywords
        partial_matches = 0
        for pk in paper_kw:
            for ek in expert_kw:
                if ek in pk or pk in ek:
                    if ek != pk:  # Not already counted as exact
                        partial_matches += 0.5
                        break

        total_match = exact_matches + partial_matches
        max_possible = max(len(paper_kw), len(expert_kw))

        return round(min(total_match / max_possible, 1.0), 3)

    def detect_conflict_of_interest(self, paper_authors, paper_affiliation=''):
        """
        Detect potential conflicts of interest between reviewer and paper authors.
        Checks for affiliation overlap and co-authorship indicators.

        Args:
            paper_authors (list): List of author name strings.
            paper_affiliation (str): Affiliation of the paper's authors.

        Returns:
            dict: Conflict detection result with details.
        """
        conflicts = []

        # Check affiliation conflict
        if (self.affiliation and paper_affiliation and
                self.affiliation.lower().strip() == paper_affiliation.lower().strip()):
            conflicts.append({
                'type': 'affiliation',
                'detail': f'Reviewer and author share affiliation: {self.affiliation}'
            })

        # Check for name-based conflicts (same last name heuristic)
        reviewer_last = self.name.split()[-1].lower() if self.name else ''
        for author in paper_authors:
            author_last = author.split()[-1].lower() if author else ''
            if reviewer_last and author_last and reviewer_last == author_last:
                conflicts.append({
                    'type': 'name_match',
                    'detail': f'Reviewer last name matches author: {author}'
                })

        # Check email domain overlap
        reviewer_domain = self.email.split('@')[-1].lower() if '@' in self.email else ''
        if reviewer_domain and paper_affiliation:
            if reviewer_domain.split('.')[0] in paper_affiliation.lower():
                conflicts.append({
                    'type': 'email_domain',
                    'detail': f'Reviewer email domain matches paper affiliation'
                })

        has_conflict = len(conflicts) > 0
        return {
            'has_conflict': has_conflict,
            'conflicts': conflicts,
            'reviewer': self.name,
            'checked_at': datetime.utcnow().isoformat()
        }

    def is_available(self):
        """
        Check if the reviewer can accept more review assignments.

        Returns:
            bool: True if the reviewer has capacity for more reviews.
        """
        return len(self.current_assignments) < self.max_reviews

    def assign_paper(self, paper_id):
        """
        Assign a paper to this reviewer for review.

        Args:
            paper_id: Identifier of the paper to assign.

        Returns:
            bool: True if assignment was successful, False if at capacity.
        """
        if not self.is_available():
            return False

        if paper_id not in self.current_assignments:
            self.current_assignments.append(paper_id)
        return True

    def complete_review(self, paper_id):
        """
        Mark a review as completed and move it from current to completed.

        Args:
            paper_id: Identifier of the reviewed paper.

        Returns:
            bool: True if the review was found and marked complete.
        """
        if paper_id in self.current_assignments:
            self.current_assignments.remove(paper_id)
            self.completed_reviews.append(paper_id)
            return True
        return False

    def get_workload_score(self):
        """
        Calculate a workload score for fair assignment distribution.
        Lower score means the reviewer has more capacity.

        Returns:
            float: Workload score between 0.0 (empty) and 1.0 (full).
        """
        if self.max_reviews == 0:
            return 1.0
        return round(len(self.current_assignments) / self.max_reviews, 3)

    @staticmethod
    def optimize_assignments(reviewers, papers_with_keywords):
        """
        Optimize reviewer-paper assignments across multiple papers.
        Uses a greedy algorithm to maximize expertise match while
        balancing workload and avoiding conflicts.

        Args:
            reviewers (list): List of Reviewer instances.
            papers_with_keywords (list): List of dicts with 'id', 'keywords',
                                        'authors', 'affiliation'.

        Returns:
            list: List of assignment dicts with reviewer, paper_id, and match score.
        """
        assignments = []

        for paper in papers_with_keywords:
            paper_id = paper.get('id')
            keywords = paper.get('keywords', [])
            authors = paper.get('authors', [])
            affiliation = paper.get('affiliation', '')

            # Score all available reviewers for this paper
            candidates = []
            for reviewer in reviewers:
                if not reviewer.is_available():
                    continue

                conflict = reviewer.detect_conflict_of_interest(authors, affiliation)
                if conflict['has_conflict']:
                    continue

                match_score = reviewer.calculate_expertise_match(keywords)
                workload = reviewer.get_workload_score()
                # Combined score: high expertise match + low workload
                combined_score = match_score * 0.7 + (1 - workload) * 0.3

                candidates.append({
                    'reviewer': reviewer,
                    'match_score': match_score,
                    'combined_score': round(combined_score, 3)
                })

            # Sort by combined score descending and assign top candidates
            candidates.sort(key=lambda x: x['combined_score'], reverse=True)

            for candidate in candidates[:3]:  # Assign up to 3 reviewers per paper
                reviewer = candidate['reviewer']
                if reviewer.assign_paper(paper_id):
                    assignments.append({
                        'paper_id': paper_id,
                        'reviewer_name': reviewer.name,
                        'reviewer_email': reviewer.email,
                        'match_score': candidate['match_score'],
                        'combined_score': candidate['combined_score']
                    })

        return assignments

    def get_profile(self):
        """
        Return a summary of the reviewer's profile and workload.

        Returns:
            dict: Reviewer profile information.
        """
        return {
            'name': self.name,
            'email': self.email,
            'expertise_areas': self.expertise_areas,
            'affiliation': self.affiliation,
            'max_reviews': self.max_reviews,
            'current_assignments': len(self.current_assignments),
            'completed_reviews': len(self.completed_reviews),
            'available': self.is_available(),
            'workload_score': self.get_workload_score()
        }

    def __repr__(self):
        return f'Reviewer("{self.name}", expertise={len(self.expertise_areas)})'
