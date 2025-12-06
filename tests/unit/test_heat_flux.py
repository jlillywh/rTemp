"""
Unit tests for heat flux calculations.

Tests all heat flux components including evaporation, convection,
sediment conduction, hyporheic exchange, groundwater flux, and
longwave back radiation.
"""

import pytest
import math
from rtemp.heat_flux import HeatFluxCalculator
from rtemp.constants import BOWEN_RATIO, WATER_EMISSIVITY, STEFAN_BOLTZMANN, CELSIUS_TO_KELVIN


class TestEvaporation:
    """Tests for evaporation flux calculation."""
    
    def test_evaporation_typical_conditions(self):
        """Test evaporation under typical conditions (water warmer than air)."""
        wind_function = 15.0  # cal/(cm²·day·mmHg)
        vapor_pressure_water = 20.0  # mmHg
        vapor_pressure_air = 15.0  # mmHg
        
        evap = HeatFluxCalculator.calculate_evaporation(
            wind_function, vapor_pressure_water, vapor_pressure_air
        )
        
        # Should be negative (heat loss)
        assert evap < 0
        # Should equal -f(W) * (e_water - e_air)
        expected = -15.0 * (20.0 - 15.0)
        assert evap == pytest.approx(expected)
    
    def test_evaporation_condensation(self):
        """Test condensation when air vapor pressure exceeds water vapor pressure."""
        wind_function = 15.0
        vapor_pressure_water = 10.0  # mmHg
        vapor_pressure_air = 15.0  # mmHg
        
        evap = HeatFluxCalculator.calculate_evaporation(
            wind_function, vapor_pressure_water, vapor_pressure_air
        )
        
        # Should be positive (heat gain from condensation)
        assert evap > 0
    
    def test_evaporation_no_gradient(self):
        """Test evaporation when vapor pressures are equal."""
        wind_function = 15.0
        vapor_pressure = 15.0
        
        evap = HeatFluxCalculator.calculate_evaporation(
            wind_function, vapor_pressure, vapor_pressure
        )
        
        # Should be zero (no flux)
        assert evap == 0.0


class TestConvection:
    """Tests for convection flux calculation."""
    
    def test_convection_typical_conditions(self):
        """Test convection under typical conditions (water warmer than air)."""
        wind_function = 15.0  # cal/(cm²·day·mmHg)
        water_temp = 20.0  # °C
        air_temp = 15.0  # °C
        
        conv = HeatFluxCalculator.calculate_convection(
            wind_function, water_temp, air_temp
        )
        
        # Should be negative (heat loss)
        assert conv < 0
        # Should equal -Bowen * f(W) * (T_water - T_air)
        expected = -BOWEN_RATIO * 15.0 * (20.0 - 15.0)
        assert conv == pytest.approx(expected)
    
    def test_convection_heat_gain(self):
        """Test convection when air is warmer than water."""
        wind_function = 15.0
        water_temp = 10.0  # °C
        air_temp = 20.0  # °C
        
        conv = HeatFluxCalculator.calculate_convection(
            wind_function, water_temp, air_temp
        )
        
        # Should be positive (heat gain)
        assert conv > 0
    
    def test_convection_no_gradient(self):
        """Test convection when temperatures are equal."""
        wind_function = 15.0
        temp = 15.0
        
        conv = HeatFluxCalculator.calculate_convection(
            wind_function, temp, temp
        )
        
        # Should be zero (no flux)
        assert conv == 0.0
    
    def test_convection_custom_bowen_ratio(self):
        """Test convection with custom Bowen ratio."""
        wind_function = 15.0
        water_temp = 20.0
        air_temp = 15.0
        custom_bowen = 0.5
        
        conv = HeatFluxCalculator.calculate_convection(
            wind_function, water_temp, air_temp, bowen_ratio=custom_bowen
        )
        
        expected = -custom_bowen * 15.0 * (20.0 - 15.0)
        assert conv == pytest.approx(expected)


class TestLongwaveBack:
    """Tests for longwave back radiation calculation."""
    
    def test_longwave_back_typical_temp(self):
        """Test longwave back radiation at typical water temperature."""
        water_temp = 20.0  # °C
        
        back = HeatFluxCalculator.calculate_longwave_back(water_temp)
        
        # Should be negative (heat loss)
        assert back < 0
        
        # Verify calculation
        water_temp_k = water_temp + CELSIUS_TO_KELVIN
        expected_w_m2 = WATER_EMISSIVITY * STEFAN_BOLTZMANN * (water_temp_k ** 4)
        # Convert to cal/(cm²·day)
        expected = -expected_w_m2 * 86400.0 / (4.183076 * 10000.0)
        assert back == pytest.approx(expected, rel=1e-6)
    
    def test_longwave_back_increases_with_temp(self):
        """Test that longwave back radiation increases with temperature."""
        back_10 = HeatFluxCalculator.calculate_longwave_back(10.0)
        back_20 = HeatFluxCalculator.calculate_longwave_back(20.0)
        back_30 = HeatFluxCalculator.calculate_longwave_back(30.0)
        
        # Higher temperature = more radiation = more negative flux
        assert back_10 > back_20 > back_30
    
    def test_longwave_back_zero_celsius(self):
        """Test longwave back radiation at 0°C."""
        back = HeatFluxCalculator.calculate_longwave_back(0.0)
        
        # Should still be negative
        assert back < 0


class TestSedimentConduction:
    """Tests for sediment conduction flux calculation."""
    
    def test_sediment_conduction_heat_gain(self):
        """Test sediment conduction when sediment is warmer than water."""
        water_temp = 15.0  # °C
        sediment_temp = 20.0  # °C
        thermal_conductivity = 0.6  # W/(m·°C)
        sediment_thickness = 10.0  # cm
        
        flux = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, sediment_thickness
        )
        
        # Should be positive (heat gain from sediment)
        assert flux > 0
    
    def test_sediment_conduction_heat_loss(self):
        """Test sediment conduction when water is warmer than sediment."""
        water_temp = 20.0  # °C
        sediment_temp = 15.0  # °C
        thermal_conductivity = 0.6  # W/(m·°C)
        sediment_thickness = 10.0  # cm
        
        flux = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, sediment_thickness
        )
        
        # Should be negative (heat loss to sediment)
        assert flux < 0
    
    def test_sediment_conduction_no_gradient(self):
        """Test sediment conduction when temperatures are equal."""
        temp = 15.0
        thermal_conductivity = 0.6
        sediment_thickness = 10.0
        
        flux = HeatFluxCalculator.calculate_sediment_conduction(
            temp, temp, thermal_conductivity, sediment_thickness
        )
        
        # Should be zero (no flux)
        assert flux == 0.0
    
    def test_sediment_conduction_zero_conductivity(self):
        """Test sediment conduction with zero thermal conductivity."""
        water_temp = 15.0
        sediment_temp = 20.0
        thermal_conductivity = 0.0
        sediment_thickness = 10.0
        
        flux = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, sediment_thickness
        )
        
        # Should be zero (no conduction)
        assert flux == 0.0
    
    def test_sediment_conduction_thickness_effect(self):
        """Test that thicker sediment reduces conduction."""
        water_temp = 15.0
        sediment_temp = 20.0
        thermal_conductivity = 0.6
        
        flux_thin = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, 5.0
        )
        flux_thick = HeatFluxCalculator.calculate_sediment_conduction(
            water_temp, sediment_temp, thermal_conductivity, 20.0
        )
        
        # Thicker sediment should reduce flux
        assert abs(flux_thin) > abs(flux_thick)


class TestHyporheicExchange:
    """Tests for hyporheic exchange flux calculation."""
    
    def test_hyporheic_exchange_heat_gain(self):
        """Test hyporheic exchange when sediment is warmer than water."""
        water_temp = 15.0  # °C
        sediment_temp = 20.0  # °C
        exchange_rate = 10.0  # cm/day
        water_depth = 1.0  # meters
        
        flux = HeatFluxCalculator.calculate_hyporheic_exchange(
            water_temp, sediment_temp, exchange_rate, water_depth
        )
        
        # Should be positive (heat gain)
        assert flux > 0
    
    def test_hyporheic_exchange_heat_loss(self):
        """Test hyporheic exchange when water is warmer than sediment."""
        water_temp = 20.0  # °C
        sediment_temp = 15.0  # °C
        exchange_rate = 10.0  # cm/day
        water_depth = 1.0  # meters
        
        flux = HeatFluxCalculator.calculate_hyporheic_exchange(
            water_temp, sediment_temp, exchange_rate, water_depth
        )
        
        # Should be negative (heat loss)
        assert flux < 0
    
    def test_hyporheic_exchange_no_exchange(self):
        """Test hyporheic exchange with zero exchange rate."""
        water_temp = 15.0
        sediment_temp = 20.0
        exchange_rate = 0.0
        water_depth = 1.0
        
        flux = HeatFluxCalculator.calculate_hyporheic_exchange(
            water_temp, sediment_temp, exchange_rate, water_depth
        )
        
        # Should be zero (no exchange)
        assert flux == 0.0
    
    def test_hyporheic_exchange_depth_effect(self):
        """Test that deeper water reduces hyporheic exchange flux."""
        water_temp = 15.0
        sediment_temp = 20.0
        exchange_rate = 10.0
        
        flux_shallow = HeatFluxCalculator.calculate_hyporheic_exchange(
            water_temp, sediment_temp, exchange_rate, 0.5
        )
        flux_deep = HeatFluxCalculator.calculate_hyporheic_exchange(
            water_temp, sediment_temp, exchange_rate, 2.0
        )
        
        # Deeper water should reduce flux per unit area
        assert abs(flux_shallow) > abs(flux_deep)


class TestGroundwaterFlux:
    """Tests for groundwater flux calculation."""
    
    def test_groundwater_flux_heat_gain(self):
        """Test groundwater flux when groundwater is warmer than water."""
        water_temp = 15.0  # °C
        groundwater_temp = 20.0  # °C
        inflow_rate = 5.0  # cm/day
        water_depth = 1.0  # meters
        
        flux = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, water_depth
        )
        
        # Should be positive (heat gain)
        assert flux > 0
    
    def test_groundwater_flux_heat_loss(self):
        """Test groundwater flux when water is warmer than groundwater."""
        water_temp = 20.0  # °C
        groundwater_temp = 15.0  # °C
        inflow_rate = 5.0  # cm/day
        water_depth = 1.0  # meters
        
        flux = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, water_depth
        )
        
        # Should be negative (heat loss)
        assert flux < 0
    
    def test_groundwater_flux_no_inflow(self):
        """Test groundwater flux with zero inflow rate."""
        water_temp = 15.0
        groundwater_temp = 20.0
        inflow_rate = 0.0
        water_depth = 1.0
        
        flux = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, water_depth
        )
        
        # Should be zero (no inflow)
        assert flux == 0.0
    
    def test_groundwater_flux_depth_effect(self):
        """Test that deeper water reduces groundwater flux."""
        water_temp = 15.0
        groundwater_temp = 20.0
        inflow_rate = 5.0
        
        flux_shallow = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, 0.5
        )
        flux_deep = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, inflow_rate, 2.0
        )
        
        # Deeper water should reduce flux per unit area
        assert abs(flux_shallow) > abs(flux_deep)
    
    def test_groundwater_flux_inflow_rate_effect(self):
        """Test that higher inflow rate increases groundwater flux."""
        water_temp = 15.0
        groundwater_temp = 20.0
        water_depth = 1.0
        
        flux_low = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, 2.0, water_depth
        )
        flux_high = HeatFluxCalculator.calculate_groundwater_flux(
            water_temp, groundwater_temp, 10.0, water_depth
        )
        
        # Higher inflow should increase flux
        assert abs(flux_high) > abs(flux_low)

