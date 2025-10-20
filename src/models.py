"""
Data models for eCourts Scraper
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class CaseInfo:
    """Case information model"""
    cnr: str
    case_number: Optional[str] = None
    case_type: Optional[str] = None
    filing_date: Optional[str] = None
    registration_date: Optional[str] = None
    status: Optional[str] = None
    court_name: Optional[str] = None
    judge_name: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    listed_on: Optional[List[str]] = field(default_factory=list)
    next_hearing: Optional[str] = None

    def to_dict(self):
        return {
            'cnr': self.cnr,
            'case_number': self.case_number,
            'case_type': self.case_type,
            'filing_date': self.filing_date,
            'registration_date': self.registration_date,
            'status': self.status,
            'court_name': self.court_name,
            'judge_name': self.judge_name,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'listed_on': self.listed_on,
            'next_hearing': self.next_hearing
        }

@dataclass
class CauseListEntry:
    """Cause list entry model"""
    serial_number: str
    case_number: str
    case_type: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    advocate: Optional[str] = None

    def to_dict(self):
        return {
            'serial_number': self.serial_number,
            'case_number': self.case_number,
            'case_type': self.case_type,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'advocate': self.advocate
        }

@dataclass
class CauseList:
    """Complete cause list model"""
    date: str
    state: str
    district: str
    court_complex: str
    court_name: str
    judge_name: Optional[str] = None
    list_type: str = "Civil"  # Civil or Criminal
    entries: List[CauseListEntry] = field(default_factory=list)

    def to_dict(self):
        return {
            'date': self.date,
            'state': self.state,
            'district': self.district,
            'court_complex': self.court_complex,
            'court_name': self.court_name,
            'judge_name': self.judge_name,
            'list_type': self.list_type,
            'total_cases': len(self.entries),
            'entries': [entry.to_dict() for entry in self.entries]
        }
