require 'spec_helper'
describe 'tortuga_kit_dummyadapter' do
  context 'with default values for all parameters' do
    it { should contain_class('tortuga_kit_dummyadapter') }
  end
end
