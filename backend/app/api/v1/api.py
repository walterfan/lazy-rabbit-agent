from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    admin_recommendations,
    auth,
    cities,
    emails,
    learning,
    medical_paper,
    rbac,
    recommendations,
    scheduled,
    secretary,
    users,
    weather,
)

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include user management routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include admin routes (user management)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Include admin recommendation routes
api_router.include_router(admin_recommendations.router, prefix="/admin/recommendations", tags=["admin-recommendations"])

# Include RBAC routes (role & permission management)
api_router.include_router(rbac.router, prefix="/rbac", tags=["rbac"])

# Include city search routes
api_router.include_router(cities.router, prefix="/cities", tags=["cities"])

# Include weather routes
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])

# Include recommendations routes
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

# Include email routes
api_router.include_router(emails.router, prefix="", tags=["emails"])

# Include scheduled job routes (for cronjob)
api_router.include_router(scheduled.router, prefix="/scheduled", tags=["scheduled"])

# Include Personal Secretary routes
api_router.include_router(secretary.router, prefix="/secretary", tags=["secretary"])

# Include Learning routes
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])

# Include Medical Paper Writing Assistant routes
api_router.include_router(medical_paper.router, prefix="/medical-paper", tags=["medical-paper"])



