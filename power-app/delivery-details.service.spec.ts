import { TestBed } from '@angular/core/testing';

import { DeliveryDetailsService } from './delivery-details.service';

describe('DeliveryDetailsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: DeliveryDetailsService = TestBed.get(DeliveryDetailsService);
    expect(service).toBeTruthy();
  });
});
