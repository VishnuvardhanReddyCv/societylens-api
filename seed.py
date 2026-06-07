"""
Seed script — creates Prestige Lakeside complex with 1 admin + 3 tenants,
5 expenses, 4 issues, 3 announcements.

Usage:
    python seed.py
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app.database import AsyncSessionLocal
from app.models.complex import ApartmentComplex, Unit
from app.models.user import User, UserRole
from app.models.expense import Expense, ExpenseCategory, Vote, VoteValue
from app.models.issue import Issue, IssueStatus
from app.models.announcement import Announcement
from app.core.security import get_password_hash


async def seed():
    async with AsyncSessionLocal() as db:
        # ── Complex ──────────────────────────────────────────────────────────
        complex_obj = ApartmentComplex(
            id=str(uuid.uuid4()),
            name="Prestige Lakeside",
            address="15, Lakeside Drive, Whitefield",
            city="Bangalore",
            invite_code="482910",
        )
        db.add(complex_obj)
        await db.flush()

        # ── Units ────────────────────────────────────────────────────────────
        unit_map = {}
        for unit_number in ["A-301", "B-204", "B-102"]:
            unit = Unit(
                id=str(uuid.uuid4()),
                complex_id=complex_obj.id,
                unit_number=unit_number,
            )
            db.add(unit)
            unit_map[unit_number] = unit
        await db.flush()

        # ── Admin ────────────────────────────────────────────────────────────
        admin = User(
            id=str(uuid.uuid4()),
            complex_id=complex_obj.id,
            name="Rajan Kumar",
            email="admin@prestige.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(admin)

        # ── Tenants ──────────────────────────────────────────────────────────
        tenants_data = [
            ("Anjali Varma",  "anjali@prestige.com", "B-204"),
            ("Suresh Nair",   "suresh@prestige.com", "B-102"),
            ("Priya Menon",   "priya@prestige.com",  "A-301"),
        ]
        tenants = []
        for name, email, unit_no in tenants_data:
            tenant = User(
                id=str(uuid.uuid4()),
                complex_id=complex_obj.id,
                unit_id=unit_map[unit_no].id,
                name=name,
                email=email,
                hashed_password=get_password_hash("tenant123"),
                role=UserRole.TENANT,
            )
            db.add(tenant)
            tenants.append(tenant)
        await db.flush()

        # ── Expenses ─────────────────────────────────────────────────────────
        expenses_data = [
            (
                "Elevator AMC – Annual",
                "Annual maintenance contract for both passenger elevators",
                85000,
                ExpenseCategory.MAINTENANCE,
                30,
            ),
            (
                "Generator Diesel – May 2024",
                "Diesel refill for DG backup generator",
                12500,
                ExpenseCategory.UTILITY,
                15,
            ),
            (
                "Security Guard Salary – May",
                "Monthly salary for 2 security guards at main gate",
                28000,
                ExpenseCategory.SECURITY,
                10,
            ),
            (
                "Lobby Waterproofing",
                "Repair water seepage in basement lobby near car park",
                45000,
                ExpenseCategory.REPAIR,
                5,
            ),
            (
                "Swimming Pool Chemicals",
                "Monthly chlorine and pH balancer for the pool",
                3800,
                ExpenseCategory.AMENITY,
                2,
            ),
        ]
        created_expenses = []
        for title, desc, amount, category, days_ago in expenses_data:
            exp = Expense(
                id=str(uuid.uuid4()),
                complex_id=complex_obj.id,
                title=title,
                description=desc,
                amount=amount,
                category=category,
                created_by=admin.id,
                created_at=datetime.utcnow() - timedelta(days=days_ago),
            )
            db.add(exp)
            created_expenses.append(exp)
        await db.flush()

        # Votes on the first expense (Elevator AMC)
        vote_data = [
            (tenants[0], VoteValue.APPROVE),
            (tenants[1], VoteValue.APPROVE),
            (tenants[2], VoteValue.REJECT),
        ]
        for tenant, value in vote_data:
            db.add(
                Vote(
                    id=str(uuid.uuid4()),
                    expense_id=created_expenses[0].id,
                    user_id=tenant.id,
                    value=value,
                )
            )

        # ── Issues ───────────────────────────────────────────────────────────
        issues_data = [
            (
                "Water leakage in B-204",
                "There is water dripping from the ceiling in my bathroom. "
                "Seems to be a pipe issue from the flat above.",
                IssueStatus.OPEN,
                tenants[0],
                7,
            ),
            (
                "Street light not working – Block B",
                "The street light near Block B entrance has been off for 3 days, "
                "creating safety concerns at night.",
                IssueStatus.OPEN,
                tenants[1],
                5,
            ),
            (
                "Gym treadmill broken",
                "The treadmill in the gym makes a loud grinding noise and is unusable.",
                IssueStatus.IN_PROGRESS,
                tenants[2],
                12,
            ),
            (
                "Common area cleaning schedule",
                "Requesting a revised cleaning schedule that covers weekends as well.",
                IssueStatus.RESOLVED,
                tenants[0],
                20,
            ),
        ]
        for title, desc, status, tenant, days_ago in issues_data:
            db.add(
                Issue(
                    id=str(uuid.uuid4()),
                    complex_id=complex_obj.id,
                    raised_by=tenant.id,
                    title=title,
                    description=desc,
                    status=status,
                    created_at=datetime.utcnow() - timedelta(days=days_ago),
                    updated_at=datetime.utcnow() - timedelta(days=days_ago),
                )
            )

        # ── Announcements ────────────────────────────────────────────────────
        ann_data = [
            (
                "Annual General Body Meeting – June 15",
                "Dear Residents,\n\nThe Annual General Body Meeting is scheduled for "
                "June 15, 2024 at 10:00 AM in the Community Hall.\n\nAgenda:\n"
                "• Annual accounts review\n• Maintenance fund discussion\n"
                "• Election of new committee members\n\n"
                "Attendance is mandatory for all flat owners. Proxy forms available at the office.",
                3,
            ),
            (
                "Water Supply Disruption – June 8",
                "Due to maintenance work on the main pipeline, water supply will be "
                "disrupted on June 8 from 10 AM to 2 PM. Please store adequate water "
                "in advance. Tanker water will be arranged if required.",
                6,
            ),
            (
                "New Parking Rules – Effective Immediately",
                "All residents are requested to park only in their designated spots. "
                "Visitor parking is limited to 2 hours. Vehicles parked in fire lanes "
                "or blocking exits will be towed at the owner's expense.",
                14,
            ),
        ]
        for title, body, days_ago in ann_data:
            db.add(
                Announcement(
                    id=str(uuid.uuid4()),
                    complex_id=complex_obj.id,
                    title=title,
                    body=body,
                    created_by=admin.id,
                    created_at=datetime.utcnow() - timedelta(days=days_ago),
                )
            )

        await db.commit()

    print("✅  Seed data created successfully!")
    print()
    print("  Complex : Prestige Lakeside  |  Invite code : 482910")
    print("  Admin   : admin@prestige.com  /  admin123")
    print("  Tenants : anjali@prestige.com  /  tenant123")
    print("            suresh@prestige.com  /  tenant123")
    print("            priya@prestige.com   /  tenant123")


if __name__ == "__main__":
    asyncio.run(seed())
