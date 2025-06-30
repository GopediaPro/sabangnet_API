from decimal import Decimal, ROUND_UP


class PriceCalculator:
    @staticmethod
    def roundup_to_thousands(value: Decimal) -> Decimal:
        """천의 자리에서 올림 (roundup)"""
        return value.quantize(Decimal('1000'), rounding=ROUND_UP)
    
    @staticmethod
    def calculate_one_one_price(standard_price: Decimal) -> Decimal:
        """1+1 가격 계산"""
        # if(기준가 + 100 < 10000, roundup(기준가 * 2 + 2000, -3) - 100, roundup(기준가 * 2 + 1000, -3) - 100)
        if standard_price + 100 < 10000:
            base_price = standard_price * 2 + 2000
            rounded_price = PriceCalculator.roundup_to_thousands(base_price)
            return rounded_price - 100
        else:
            base_price = standard_price * 2 + 1000
            rounded_price = PriceCalculator.roundup_to_thousands(base_price)
            return rounded_price - 100
        
    @staticmethod 
    def calculate_shop_prices_115_percent(one_one_price: Decimal) -> Decimal:
        """115% 적용 샵들 가격 계산"""
        # roundup(1+1가격 * 1.15, -3) - 100
        base_price = one_one_price * Decimal('1.15')
        rounded_price = PriceCalculator.roundup_to_thousands(base_price)
        return rounded_price - 100
        
    @staticmethod
    def calculate_shop_prices_105_percent(one_one_price: Decimal) -> Decimal:
        """105% 적용 샵들 가격 계산"""
        # roundup(1+1가격 * 1.05, -3) - 100
        base_price = one_one_price * Decimal('1.05')
        rounded_price = PriceCalculator.roundup_to_thousands(base_price)
        return rounded_price - 100
        
    @staticmethod
    def calculate_shop_prices_plus_100(one_one_price: Decimal) -> Decimal:
        """1+1가격 + 100 적용 샵들"""
        # 1+1가격 + 100
        return one_one_price + 100