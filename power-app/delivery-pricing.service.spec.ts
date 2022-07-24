import { TestBed } from '@angular/core/testing';

import { DeliveryPricingService } from './delivery-pricing.service';

describe('PricingServiceService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: DeliveryPricingService = TestBed.get(DeliveryPricingService);
    expect(service).toBeTruthy();
  });
});
