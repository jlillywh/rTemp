"""
NOAA solar position algorithm implementation.

This module implements the NOAA solar position algorithm for calculating
solar azimuth, elevation, and related parameters.
"""

import math
from datetime import datetime
from typing import Tuple

from rtemp.constants import (
    DEG_TO_RAD,
    RAD_TO_DEG,
    J2000_EPOCH,
    MAX_LATITUDE,
    MIN_LATITUDE,
)


class NOAASolarPosition:
    """
    NOAA solar position calculator.

    Implements the NOAA algorithm for calculating solar position
    (azimuth, elevation) for any location, date, and time.
    """

    @staticmethod
    def calc_julian_day(year: int, month: int, day: int) -> float:
        """
        Calculate Julian Day from calendar date.

        Args:
            year: Year
            month: Month (1-12)
            day: Day of month

        Returns:
            Julian Day number
        """
        # Adjust for January and February being months 13 and 14 of previous year
        if month <= 2:
            year -= 1
            month += 12

        a = year // 100
        b = 2 - a + (a // 4)

        jd = (
            math.floor(365.25 * (year + 4716))
            + math.floor(30.6001 * (month + 1))
            + day
            + b
            - 1524.5
        )

        return jd

    @staticmethod
    def calc_time_julian_cent(jd: float) -> float:
        """
        Calculate time in Julian centuries since J2000.0 epoch.

        Args:
            jd: Julian Day

        Returns:
            Time in Julian centuries
        """
        return (jd - J2000_EPOCH) / 36525.0

    @staticmethod
    def calc_geom_mean_long_sun(t: float) -> float:
        """
        Calculate geometric mean longitude of the sun.

        Args:
            t: Time in Julian centuries

        Returns:
            Geometric mean longitude in degrees
        """
        l0 = 280.46646 + t * (36000.76983 + t * 0.0003032)
        # Normalize to 0-360
        l0 = l0 % 360.0
        return l0

    @staticmethod
    def calc_geom_mean_anomaly_sun(t: float) -> float:
        """
        Calculate geometric mean anomaly of the sun.

        Args:
            t: Time in Julian centuries

        Returns:
            Geometric mean anomaly in degrees
        """
        m = 357.52911 + t * (35999.05029 - 0.0001537 * t)
        return m

    @staticmethod
    def calc_eccentricity_earth_orbit(t: float) -> float:
        """
        Calculate eccentricity of Earth's orbit.

        Args:
            t: Time in Julian centuries

        Returns:
            Eccentricity (dimensionless)
        """
        e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
        return e

    @staticmethod
    def calc_sun_eq_of_center(t: float) -> float:
        """
        Calculate equation of center for the sun.

        Args:
            t: Time in Julian centuries

        Returns:
            Equation of center in degrees
        """
        m = NOAASolarPosition.calc_geom_mean_anomaly_sun(t)
        mrad = m * DEG_TO_RAD

        sinm = math.sin(mrad)
        sin2m = math.sin(2 * mrad)
        sin3m = math.sin(3 * mrad)

        c = (
            sinm * (1.914602 - t * (0.004817 + 0.000014 * t))
            + sin2m * (0.019993 - 0.000101 * t)
            + sin3m * 0.000289
        )

        return c

    @staticmethod
    def calc_sun_true_long(t: float) -> float:
        """
        Calculate sun's true longitude.

        Args:
            t: Time in Julian centuries

        Returns:
            True longitude in degrees
        """
        l0 = NOAASolarPosition.calc_geom_mean_long_sun(t)
        c = NOAASolarPosition.calc_sun_eq_of_center(t)
        return l0 + c

    @staticmethod
    def calc_sun_apparent_long(t: float) -> float:
        """
        Calculate sun's apparent longitude.

        Args:
            t: Time in Julian centuries

        Returns:
            Apparent longitude in degrees
        """
        o = NOAASolarPosition.calc_sun_true_long(t)
        omega = 125.04 - 1934.136 * t
        lambda_sun = o - 0.00569 - 0.00478 * math.sin(omega * DEG_TO_RAD)
        return lambda_sun

    @staticmethod
    def calc_mean_obliquity_ecliptic(t: float) -> float:
        """
        Calculate mean obliquity of the ecliptic.

        Args:
            t: Time in Julian centuries

        Returns:
            Mean obliquity in degrees
        """
        seconds = 21.448 - t * (46.8150 + t * (0.00059 - t * 0.001813))
        e0 = 23.0 + (26.0 + (seconds / 60.0)) / 60.0
        return e0

    @staticmethod
    def calc_obliquity_correction(t: float) -> float:
        """
        Calculate corrected obliquity of the ecliptic.

        Args:
            t: Time in Julian centuries

        Returns:
            Corrected obliquity in degrees
        """
        e0 = NOAASolarPosition.calc_mean_obliquity_ecliptic(t)
        omega = 125.04 - 1934.136 * t
        e = e0 + 0.00256 * math.cos(omega * DEG_TO_RAD)
        return e

    @staticmethod
    def calc_sun_rt_ascension(t: float) -> float:
        """
        Calculate sun's right ascension.

        Args:
            t: Time in Julian centuries

        Returns:
            Right ascension in degrees
        """
        e = NOAASolarPosition.calc_obliquity_correction(t)
        lambda_sun = NOAASolarPosition.calc_sun_apparent_long(t)

        tananum = math.cos(e * DEG_TO_RAD) * math.sin(lambda_sun * DEG_TO_RAD)
        tanadenom = math.cos(lambda_sun * DEG_TO_RAD)

        alpha = math.atan2(tananum, tanadenom) * RAD_TO_DEG
        return alpha

    @staticmethod
    def calc_sun_declination(t: float) -> float:
        """
        Calculate sun's declination.

        Args:
            t: Time in Julian centuries

        Returns:
            Declination in degrees
        """
        e = NOAASolarPosition.calc_obliquity_correction(t)
        lambda_sun = NOAASolarPosition.calc_sun_apparent_long(t)

        sint = math.sin(e * DEG_TO_RAD) * math.sin(lambda_sun * DEG_TO_RAD)
        theta = math.asin(sint) * RAD_TO_DEG
        return theta

    @staticmethod
    def calc_equation_of_time(t: float) -> float:
        """
        Calculate equation of time.

        Args:
            t: Time in Julian centuries

        Returns:
            Equation of time in minutes
        """
        epsilon = NOAASolarPosition.calc_obliquity_correction(t)
        l0 = NOAASolarPosition.calc_geom_mean_long_sun(t)
        e = NOAASolarPosition.calc_eccentricity_earth_orbit(t)
        m = NOAASolarPosition.calc_geom_mean_anomaly_sun(t)

        y = math.tan((epsilon / 2.0) * DEG_TO_RAD) ** 2

        sin2l0 = math.sin(2.0 * l0 * DEG_TO_RAD)
        sinm = math.sin(m * DEG_TO_RAD)
        cos2l0 = math.cos(2.0 * l0 * DEG_TO_RAD)
        sin4l0 = math.sin(4.0 * l0 * DEG_TO_RAD)
        sin2m = math.sin(2.0 * m * DEG_TO_RAD)

        etime = (
            y * sin2l0
            - 2.0 * e * sinm
            + 4.0 * e * y * sinm * cos2l0
            - 0.5 * y * y * sin4l0
            - 1.25 * e * e * sin2m
        )

        return etime * RAD_TO_DEG * 4.0  # Convert to minutes

    @staticmethod
    def calc_sun_rad_vector(t: float) -> float:
        """
        Calculate Earth-Sun distance in AU.

        Args:
            t: Time in Julian centuries

        Returns:
            Distance in astronomical units
        """
        v = NOAASolarPosition.calc_sun_true_long(t)
        e = NOAASolarPosition.calc_eccentricity_earth_orbit(t)

        r = (1.000001018 * (1 - e * e)) / (1 + e * math.cos(v * DEG_TO_RAD))
        return r

    @staticmethod
    def calc_solar_position(
        lat: float, lon: float, dt: datetime, timezone: float, dlstime: int
    ) -> Tuple[float, float, float]:
        """
        Calculate solar position for given location and time.

        Args:
            lat: Latitude in degrees (positive north)
            lon: Longitude in degrees (positive east, negative west)
            dt: Datetime object
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset (0 or 1)

        Returns:
            Tuple of (azimuth, elevation, earth_sun_distance)
            - azimuth: degrees from north
            - elevation: degrees above horizon
            - earth_sun_distance: distance in AU
        """
        # Clamp latitude to valid range (Requirement 17.6, 17.7)
        lat = max(MIN_LATITUDE, min(MAX_LATITUDE, lat))

        # Note: longitude and timezone should remain negative for western hemisphere
        # The NOAA algorithm uses negative values for west longitude and west timezones

        # Calculate Julian Day
        jd = NOAASolarPosition.calc_julian_day(dt.year, dt.month, dt.day)

        # Add time of day as fraction
        time_fraction = (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
        jd += time_fraction

        # Calculate Julian century
        t = NOAASolarPosition.calc_time_julian_cent(jd)

        # Calculate equation of time
        eq_time = NOAASolarPosition.calc_equation_of_time(t)

        # Calculate solar declination
        decl = NOAASolarPosition.calc_sun_declination(t)

        # Calculate true solar time in minutes
        time_offset = eq_time + 4.0 * lon - 60.0 * timezone - 60.0 * dlstime
        true_solar_time = (dt.hour * 60.0 + dt.minute + dt.second / 60.0) + time_offset

        # Handle true solar time > 1440 (Requirement 17.8)
        while true_solar_time > 1440:
            true_solar_time -= 1440

        # Calculate hour angle
        hour_angle = (true_solar_time / 4.0) - 180.0

        # Handle hour angle < -180 (Requirement 17.9)
        while hour_angle < -180:
            hour_angle += 360

        # Calculate solar zenith angle
        lat_rad = lat * DEG_TO_RAD
        decl_rad = decl * DEG_TO_RAD
        ha_rad = hour_angle * DEG_TO_RAD

        cos_zenith = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(
            decl_rad
        ) * math.cos(ha_rad)

        # Clamp cosine to valid range (Requirement 17.10, 17.11)
        cos_zenith = max(-1.0, min(1.0, cos_zenith))

        zenith = math.acos(cos_zenith) * RAD_TO_DEG

        # Calculate solar elevation with atmospheric refraction correction
        elevation = 90.0 - zenith

        if elevation > 85.0:
            refraction = 0.0
        else:
            te = math.tan(elevation * DEG_TO_RAD)
            if elevation > 5.0:
                refraction = 58.1 / te - 0.07 / (te**3) + 0.000086 / (te**5)
            elif elevation > -0.575:
                refraction = 1735.0 + elevation * (
                    -518.2 + elevation * (103.4 + elevation * (-12.79 + elevation * 0.711))
                )
            else:
                refraction = -20.772 / te
            refraction = refraction / 3600.0

        elevation += refraction

        # Calculate solar azimuth (degrees from North, clockwise)
        # Formula: azimuth = 180 - acos(cos_azimuth)
        cos_azimuth = ((math.sin(lat_rad) * math.cos(zenith * DEG_TO_RAD)) - math.sin(decl_rad)) / (
            math.cos(lat_rad) * math.sin(zenith * DEG_TO_RAD)
        )

        # Clamp cosine to valid range (Requirement 17.10, 17.11)
        cos_azimuth = max(-1.0, min(1.0, cos_azimuth))

        # Calculate azimuth using VBA-compatible formula
        azimuth = 180.0 - (math.acos(cos_azimuth) * RAD_TO_DEG)

        # Adjust azimuth based on hour angle
        if hour_angle > 0:
            azimuth = -azimuth

        # Normalize to 0-360 range
        if azimuth < 0:
            azimuth = azimuth + 360.0

        # Calculate Earth-Sun distance
        distance = NOAASolarPosition.calc_sun_rad_vector(t)

        return (azimuth, elevation, distance)

    @staticmethod
    def calc_sunrise(
        lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
    ) -> float:
        """
        Calculate sunrise time.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset

        Returns:
            Sunrise time as fraction of day (0-1)
        """
        # Clamp latitude to valid range
        lat = max(MIN_LATITUDE, min(MAX_LATITUDE, lat))

        # Convert longitude to positive for western hemisphere
        if lon < 0:
            lon = -lon

        # Convert timezone to positive for western hemisphere
        if timezone < 0:
            timezone = -timezone

        # Calculate Julian Day
        jd = NOAASolarPosition.calc_julian_day(year, month, day)
        t = NOAASolarPosition.calc_time_julian_cent(jd)

        # First pass
        eq_time = NOAASolarPosition.calc_equation_of_time(t)
        decl = NOAASolarPosition.calc_sun_declination(t)

        ha = NOAASolarPosition.calc_hour_angle_sunrise(lat, decl)

        sunrise_utc = 720 - 4 * (lon + ha) - eq_time

        # Second pass with refined time
        jd_sunrise = jd + sunrise_utc / 1440.0
        t_sunrise = NOAASolarPosition.calc_time_julian_cent(jd_sunrise)

        eq_time = NOAASolarPosition.calc_equation_of_time(t_sunrise)
        decl = NOAASolarPosition.calc_sun_declination(t_sunrise)

        ha = NOAASolarPosition.calc_hour_angle_sunrise(lat, decl)

        sunrise_utc = 720 - 4 * (lon + ha) - eq_time

        # Convert to local time
        sunrise_local = sunrise_utc + timezone * 60 + dlstime * 60

        # Return as fraction of day
        return sunrise_local / 1440.0

    @staticmethod
    def calc_sunset(
        lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
    ) -> float:
        """
        Calculate sunset time.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset

        Returns:
            Sunset time as fraction of day (0-1)
        """
        # Clamp latitude to valid range
        lat = max(MIN_LATITUDE, min(MAX_LATITUDE, lat))

        # Convert longitude to positive for western hemisphere
        if lon < 0:
            lon = -lon

        # Convert timezone to positive for western hemisphere
        if timezone < 0:
            timezone = -timezone

        # Calculate Julian Day
        jd = NOAASolarPosition.calc_julian_day(year, month, day)
        t = NOAASolarPosition.calc_time_julian_cent(jd)

        # First pass
        eq_time = NOAASolarPosition.calc_equation_of_time(t)
        decl = NOAASolarPosition.calc_sun_declination(t)

        ha = NOAASolarPosition.calc_hour_angle_sunset(lat, decl)

        sunset_utc = 720 - 4 * (lon - ha) - eq_time

        # Second pass with refined time
        jd_sunset = jd + sunset_utc / 1440.0
        t_sunset = NOAASolarPosition.calc_time_julian_cent(jd_sunset)

        eq_time = NOAASolarPosition.calc_equation_of_time(t_sunset)
        decl = NOAASolarPosition.calc_sun_declination(t_sunset)

        ha = NOAASolarPosition.calc_hour_angle_sunset(lat, decl)

        sunset_utc = 720 - 4 * (lon - ha) - eq_time

        # Convert to local time
        sunset_local = sunset_utc + timezone * 60 + dlstime * 60

        # Return as fraction of day
        return sunset_local / 1440.0

    @staticmethod
    def calc_hour_angle_sunrise(lat: float, decl: float) -> float:
        """
        Calculate hour angle at sunrise.

        Args:
            lat: Latitude in degrees
            decl: Solar declination in degrees

        Returns:
            Hour angle in degrees
        """
        lat_rad = lat * DEG_TO_RAD
        decl_rad = decl * DEG_TO_RAD

        cos_ha = (
            math.cos(90.833 * DEG_TO_RAD) / (math.cos(lat_rad) * math.cos(decl_rad))
        ) - math.tan(lat_rad) * math.tan(decl_rad)

        # Clamp to valid range
        cos_ha = max(-1.0, min(1.0, cos_ha))

        ha = math.acos(cos_ha) * RAD_TO_DEG
        return ha

    @staticmethod
    def calc_hour_angle_sunset(lat: float, decl: float) -> float:
        """
        Calculate hour angle at sunset.

        Args:
            lat: Latitude in degrees
            decl: Solar declination in degrees

        Returns:
            Hour angle in degrees
        """
        # Sunset hour angle is negative of sunrise hour angle
        return NOAASolarPosition.calc_hour_angle_sunrise(lat, decl)

    @staticmethod
    def calc_solar_noon_utc(lon: float, year: int, month: int, day: int) -> float:
        """
        Calculate solar noon in UTC.

        Args:
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day

        Returns:
            Solar noon time in minutes from midnight UTC
        """
        # Convert longitude to positive for western hemisphere
        if lon < 0:
            lon = -lon

        jd = NOAASolarPosition.calc_julian_day(year, month, day)
        t = NOAASolarPosition.calc_time_julian_cent(jd)

        eq_time = NOAASolarPosition.calc_equation_of_time(t)

        solar_noon_utc = 720 - 4 * lon - eq_time

        return solar_noon_utc

    @staticmethod
    def sunrise(
        lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
    ) -> float:
        """
        Wrapper function for calculating sunrise time.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset

        Returns:
            Sunrise time as fraction of day (0-1)
        """
        return NOAASolarPosition.calc_sunrise(lat, lon, year, month, day, timezone, dlstime)

    @staticmethod
    def sunset(
        lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
    ) -> float:
        """
        Wrapper function for calculating sunset time.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset

        Returns:
            Sunset time as fraction of day (0-1)
        """
        return NOAASolarPosition.calc_sunset(lat, lon, year, month, day, timezone, dlstime)

    @staticmethod
    def solarnoon(
        lat: float, lon: float, year: int, month: int, day: int, timezone: float, dlstime: int
    ) -> float:
        """
        Wrapper function for calculating solar noon time.

        Args:
            lat: Latitude in degrees (not used but kept for consistency)
            lon: Longitude in degrees
            year: Year
            month: Month
            day: Day
            timezone: Timezone offset from UTC in hours (negative for west)
            dlstime: Daylight savings time offset

        Returns:
            Solar noon time as fraction of day (0-1)
        """
        solar_noon_utc = NOAASolarPosition.calc_solar_noon_utc(lon, year, month, day)

        # Convert timezone to positive for western hemisphere
        if timezone < 0:
            timezone = -timezone

        # Convert to local time
        solar_noon_local = solar_noon_utc + timezone * 60 + dlstime * 60

        # Return as fraction of day
        return solar_noon_local / 1440.0
